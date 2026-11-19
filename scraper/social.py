"""Post new roles to the owner's Telegram channel and LinkedIn page.

Both stay quiet until the owner adds secrets. A missing account is not a
failed scrape.
"""

from __future__ import annotations

import json
import os
from html import escape
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from scraper.http_util import UA
from scraper.models import Job
from scraper.slug import job_page

MAX_POSTS = 8

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
     -H "LinkedIn-Version: 202511" \\
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


def announce(jobs: list[Job]) -> None:
    """Post up to eight new roles. Never raises; the scrape should still publish."""
    if not jobs:
        print("No new jobs to post.")
        return
    shown = jobs[:MAX_POSTS]
    extra = len(jobs) - len(shown)
    try:
        _telegram(shown, extra)
    except Exception as exc:
        print(f"Telegram post failed: {type(exc).__name__}")
    try:
        _linkedin(shown, extra)
    except Exception as exc:
        print(f"LinkedIn post failed: {type(exc).__name__}")


def telegram_text(jobs: list[Job], extra: int) -> str:
    lines = ["<b>New visa-sponsored roles</b>"]
    for job in jobs:
        where = f" ({escape(job.location)})" if job.location else ""
        reloc = " · relocation" if job.reloc else ""
        lines.append(
            f"• <b>{escape(job.position)}</b> — {escape(job.company)}{where}\n"
            f"  {escape(job.sponsorship_evidence)}{reloc}\n"
            f"  {escape(job_page(job))}"
        )
    if extra:
        lines.append(f"\nAnd {extra} more on https://visajobs.xyz/visa-sponsored-jobs/")
    return "\n".join(lines)[:4000]


def linkedin_text(jobs: list[Job], extra: int) -> str:
    lines = ["New visa-sponsored roles on visajobs.xyz"]
    for job in jobs:
        where = f" ({job.location})" if job.location else ""
        reloc = " · relocation" if job.reloc else ""
        lines.append(
            f"• {job.position} — {job.company}{where} [{job.sponsorship_evidence}{reloc}]\n"
            f"  {job_page(job)}"
        )
    if extra:
        lines.append(f"And {extra} more: https://visajobs.xyz/visa-sponsored-jobs/")
    return "\n".join(lines)[:2900]


def _telegram(jobs: list[Job], extra: int) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        print(TELEGRAM_HELP)
        return
    _post_form(
        f"https://api.telegram.org/bot{token}/sendMessage",
        {
            "chat_id": chat,
            "text": telegram_text(jobs, extra),
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        },
    )
    print(f"Posted {len(jobs)} jobs to Telegram.")


def _linkedin(jobs: list[Job], extra: int) -> None:
    org = os.environ.get("LINKEDIN_ORGANIZATION_ID", "").strip()
    access = _linkedin_token()
    if not access or not org:
        print(LINKEDIN_HELP)
        return
    version = os.environ.get("LINKEDIN_VERSION", "202511")
    payload = {
        "author": f"urn:li:organization:{org}",
        "commentary": linkedin_text(jobs, extra),
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
    print(f"Posted {len(jobs)} jobs to LinkedIn.")


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
