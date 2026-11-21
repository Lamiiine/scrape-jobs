"""Post one daily digest to Telegram and to LinkedIn.

A missing account does not fail the scrape. Roles already recorded in
data/posted-ids.json are never sent again, and each channel gets at most
one message per day.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from scraper.http_util import UA
from scraper.models import Job
from scraper.post_template import render_linkedin, render_telegram, render_telegram_preview
from scraper.urls import canonical_url, is_direct

ROOT = Path(__file__).resolve().parent.parent
POSTED_PATH = ROOT / "data" / "posted-ids.json"
MAX_ROLES = 5
CHANNELS = ("telegram", "linkedin")

TELEGRAM_HELP = """
TELEGRAM IS NOT CONNECTED
The daily run will post new roles once these Actions secrets exist on Lamiiine/scrape-jobs:

1. In Telegram, open @BotFather and send /newbot. Copy the token.
2. Add that bot as an administrator of the channel (the public one is @visa_sponsored_jobss).
3. Secret TELEGRAM_BOT_TOKEN = the token from BotFather.
4. Secret TELEGRAM_CHAT_ID = @visa_sponsored_jobss
   (or the numeric id, like -100..., if the channel has no public username).

The bot token does not expire. No further steps after the secrets are saved.
""".strip()

LINKEDIN_HELP = """
LINKEDIN IS NOT CONNECTED
LinkedIn does not let a scraper read a feed, and it will not post to a company
page until an app you own has been approved and you have signed in once.

1. Create an app at https://www.linkedin.com/developers/apps
   and add the Community Management API product (w_organization_social).
   LinkedIn has to approve that product before posting works.
2. In the app's Auth tab, add redirect URL https://visajobs.xyz/ and note the
   client id and client secret.
3. Open this URL while logged into the LinkedIn account that administers the
   company page, after replacing CLIENT_ID:

   https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=CLIENT_ID&redirect_uri=https%3A%2F%2Fvisajobs.xyz%2F&scope=w_organization_social%20rw_organization_admin

4. LinkedIn redirects to visajobs.xyz/?code=... Copy that code.
5. Exchange it once (the code expires in minutes):

   curl -s https://www.linkedin.com/oauth/v2/accessToken \\
     -d grant_type=authorization_code \\
     -d code=THE_CODE \\
     -d client_id=CLIENT_ID \\
     -d client_secret=CLIENT_SECRET \\
     -d redirect_uri=https://visajobs.xyz/

   The JSON includes refresh_token.
6. Find the company id:

   curl -s -H "Authorization: Bearer ACCESS_TOKEN" \\
     -H "LinkedIn-Version: 202611" \\
     "https://api.linkedin.com/rest/organizationAcls?q=roleAssignee"

   Use the number in urn:li:organization:NUMBER.
7. Secrets on Lamiiine/scrape-jobs:
   LINKEDIN_CLIENT_ID
   LINKEDIN_CLIENT_SECRET
   LINKEDIN_REFRESH_TOKEN
   LINKEDIN_ORGANIZATION_ID   (digits only)

The daily run exchanges the refresh token for a fresh access token, so you do
not have to sign in again until LinkedIn revokes the refresh token (about a
year). A short-lived LINKEDIN_ACCESS_TOKEN secret also works, but it dies in
about 60 days.
""".strip()


def announce(
    board: list[Job],
    fresh: list[Job] | None = None,
    *,
    today: date | None = None,
    dry_run: bool = False,
    ledger_path: Path | None = None,
    telegram_send=None,
    linkedin_send=None,
) -> None:
    """Send one digest per channel. Never raises; publishing should continue."""
    today = today or datetime.now(timezone.utc).date()
    day = today.isoformat()
    path = ledger_path or POSTED_PATH
    ledger = load_ledger(path)
    incoming = fresh if fresh is not None else board
    by_id = {}
    for job in list(board) + list(incoming):
        ident = job_id(job)
        if ident:
            by_id[ident] = job

    pending = list(ledger["pending"])
    for job in incoming:
        ident = job_id(job)
        if ident and ident not in pending and not _already(ledger, ident):
            pending.append(ident)
    pending = [ident for ident in pending if ident in by_id]

    ready = {
        "telegram": telegram_send is not None or _telegram_ready(),
        "linkedin": linkedin_send is not None or _linkedin_ready(),
    }
    sent_any = False
    for channel in CHANNELS:
        if ledger["last_post"].get(channel) == day:
            print(f"{channel}: already posted today.")
            continue
        chosen = select_roles(
            [by_id[ident] for ident in pending if ident not in _posted_set(ledger, channel)]
        )
        if not chosen:
            print(f"{channel}: no new roles.")
            continue
        if channel == "telegram":
            message = render_telegram(chosen, today)
            print(render_telegram_preview(chosen, today))
            if today.weekday() >= 5:
                print("Telegram notifications: off (weekend).")
        else:
            message = render_linkedin(chosen, today)
            print(message)
        if dry_run:
            print(f"DRY_RUN_SOCIAL: {channel} preview only, {len(chosen)} {_roles(len(chosen))}, not sent.")
            continue
        if not ready[channel]:
            print(TELEGRAM_HELP if channel == "telegram" else LINKEDIN_HELP)
            continue
        try:
            if channel == "telegram":
                (telegram_send or _telegram)(message, today)
            else:
                (linkedin_send or _linkedin)(message)
        except Exception as exc:
            print(f"{channel} post failed: {type(exc).__name__}")
            continue
        sent = _posted_set(ledger, channel)
        for job in chosen:
            sent.add(job_id(job))
        ledger["posted"][channel] = sorted(sent)
        ledger["last_post"][channel] = day
        sent_any = True
        print(f"Posted {len(chosen)} {_roles(len(chosen))} to {channel}.")

    if dry_run:
        return
    configured = [name for name in CHANNELS if ready[name]]
    if configured:
        ledger["pending"] = [
            ident
            for ident in pending
            if any(ident not in _posted_set(ledger, name) for name in configured)
        ]
    else:
        ledger["pending"] = pending
    if sent_any or ledger["pending"] != load_ledger(path)["pending"]:
        save_ledger(ledger, path)


def _roles(count: int) -> str:
    return "role" if count == 1 else "roles"


def select_roles(jobs: list[Job], limit: int = MAX_ROLES) -> list[Job]:
    """Best first: confirmed, then a salary, then a direct employer link, then newest."""
    chosen = [job for job in jobs if job_id(job)]
    chosen.sort(key=lambda job: job.posted_at or job.post_date or "", reverse=True)
    chosen.sort(key=lambda job: is_direct(job.apply_url), reverse=True)
    chosen.sort(key=lambda job: bool(job.salary), reverse=True)
    chosen.sort(key=lambda job: job.sponsorship_evidence == "confirmed", reverse=True)
    return chosen[:limit]


def job_id(job: Job) -> str:
    return canonical_url(job.apply_url)


def load_ledger(path: Path | None = None) -> dict:
    path = path or POSTED_PATH
    blank = {
        "posted": {"telegram": [], "linkedin": []},
        "pending": [],
        "last_post": {"telegram": "", "linkedin": ""},
    }
    if not path.exists():
        return blank
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return blank
    if not isinstance(raw, dict):
        return blank
    posted = raw.get("posted") if isinstance(raw.get("posted"), dict) else {}
    last = raw.get("last_post") if isinstance(raw.get("last_post"), dict) else {}
    pending = raw.get("pending") if isinstance(raw.get("pending"), list) else []
    return {
        "posted": {
            "telegram": _strings(posted.get("telegram")),
            "linkedin": _strings(posted.get("linkedin")),
        },
        "pending": _strings(pending),
        "last_post": {
            "telegram": str(last.get("telegram") or ""),
            "linkedin": str(last.get("linkedin") or ""),
        },
    }


def save_ledger(ledger: dict, path: Path | None = None) -> None:
    path = path or POSTED_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")


def telegram_fields(text: str, on: date, chat: str) -> dict:
    return {
        "chat_id": chat,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
        "disable_notification": "true" if on.weekday() >= 5 else "false",
    }


def social_dry_run(flag: bool = False) -> bool:
    if flag:
        return True
    return os.environ.get("DRY_RUN_SOCIAL", "").strip().lower() in {"1", "true", "yes", "on"}


def _posted_set(ledger: dict, channel: str) -> set[str]:
    return set(ledger["posted"].get(channel) or [])


def _already(ledger: dict, ident: str) -> bool:
    return all(ident in _posted_set(ledger, channel) for channel in CHANNELS)


def _strings(values) -> list[str]:
    if not isinstance(values, list):
        return []
    found = []
    for value in values:
        if isinstance(value, str) and value and value not in found:
            found.append(value)
    return found


def _telegram_ready() -> bool:
    return bool(os.environ.get("TELEGRAM_BOT_TOKEN", "").strip() and os.environ.get("TELEGRAM_CHAT_ID", "").strip())


def _linkedin_ready() -> bool:
    org = os.environ.get("LINKEDIN_ORGANIZATION_ID", "").strip()
    if not org:
        return False
    if os.environ.get("LINKEDIN_ACCESS_TOKEN", "").strip():
        return True
    return bool(
        os.environ.get("LINKEDIN_REFRESH_TOKEN", "").strip()
        and os.environ.get("LINKEDIN_CLIENT_ID", "").strip()
        and os.environ.get("LINKEDIN_CLIENT_SECRET", "").strip()
    )


def _telegram(text: str, on: date) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        print(TELEGRAM_HELP)
        return
    _post_form(
        f"https://api.telegram.org/bot{token}/sendMessage",
        telegram_fields(text, on, chat),
    )


def _linkedin(text: str) -> None:
    org = os.environ.get("LINKEDIN_ORGANIZATION_ID", "").strip()
    access = _linkedin_token()
    if not access or not org:
        print(LINKEDIN_HELP)
        return
    version = os.environ.get("LINKEDIN_VERSION", "202611")
    payload = {
        "author": f"urn:li:organization:{org}",
        "commentary": text[:2900],
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    _post_json(
        "https://api.linkedin.com/rest/posts",
        payload,
        {
            "Authorization": f"Bearer {access}",
            "LinkedIn-Version": version,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        },
    )


def _linkedin_token() -> str:
    refresh = os.environ.get("LINKEDIN_REFRESH_TOKEN", "").strip()
    client_id = os.environ.get("LINKEDIN_CLIENT_ID", "").strip()
    client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET", "").strip()
    if refresh and client_id and client_secret:
        payload = _post_form(
            "https://www.linkedin.com/oauth/v2/accessToken",
            {
                "grant_type": "refresh_token",
                "refresh_token": refresh,
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )
        token = str(payload.get("access_token") or "")
        if token:
            return token
    return os.environ.get("LINKEDIN_ACCESS_TOKEN", "").strip()


def _post_form(url: str, fields: dict) -> dict:
    data = urlencode(fields).encode()
    req = Request(url, data=data, headers={"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded"})
    with urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8", "replace")
    if not body:
        return {}
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return {}
    if isinstance(parsed, dict) and parsed.get("ok") is False:
        raise RuntimeError(parsed.get("description") or "request failed")
    return parsed if isinstance(parsed, dict) else {}


def _post_json(url: str, payload: dict, headers: dict) -> None:
    req = Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"User-Agent": UA, **headers},
        method="POST",
    )
    with urlopen(req, timeout=30) as response:
        status = getattr(response, "status", 200)
        if status >= 300:
            raise RuntimeError(f"HTTP {status}")
