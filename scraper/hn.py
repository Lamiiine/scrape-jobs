"""Ask HN: Who is hiring?

The monthly thread is a public list of employers who write their own offer,
often including a visa line and a link to their site. LinkedIn and X do not
expose a comparable public search.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timezone
from html import unescape

from scraper.classify import html_to_text
from scraper.http_util import fetch_json
from scraper.urls import is_aggregator, is_competitor, is_direct

ALGOLIA = (
    "https://hn.algolia.com/api/v1/search_by_date"
    "?tags=story&hitsPerPage=8&query=Ask%20HN%3A%20Who%20is%20hiring"
)
ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"

# Not an application, even though they are not competitor job boards.
SKIP_HOSTS = (
    "news.ycombinator.com",
    "ycombinator.com",
    "twitter.com",
    "x.com",
    "t.me",
    "telegram.me",
    "facebook.com",
    "instagram.com",
    "youtube.com",
    "youtu.be",
    "github.com",
    "linkedin.com",
)

HREF_RE = re.compile(r"""href=["']([^"']+)["']""", re.I)
TITLE_RE = re.compile(r"^ask hn:\s+who is hiring\?", re.I)


def parse_comment(html: str, posted_at: str) -> dict | None:
    """Turn one Who-is-hiring comment into fields for ``_build_job``."""
    if not html or not posted_at:
        return None
    text = unescape(html.replace("<p>", "\n").replace("</p>", "\n").replace("<br>", "\n"))
    hrefs = [unescape(url) for url in HREF_RE.findall(html)]
    plain = html_to_text(text)
    first = plain.split("\n", 1)[0]
    parts = [part.strip(" -") for part in first.split("|")]
    parts = [part for part in parts if part]
    if len(parts) < 2:
        return None
    company = _company_name(parts[0])
    position = parts[1].strip()
    location = parts[2].strip() if len(parts) > 2 else ""
    if not company or company == "Confidential" or not position or position.lower().startswith("http"):
        return None
    links = [url for url in hrefs if _usable(url)]
    if not links:
        return None
    return {
        "company": company[:120],
        "position": position[:160],
        "location": location[:160],
        "links": links,
        "text": plain,
        "posted_at": posted_at,
    }


def _company_name(raw: str) -> str:
    name = re.sub(r"\s*\([^)]*(?:https?:|YC)[^)]*\)", " ", raw, flags=re.I)
    name = re.split(r"https?://", name, maxsplit=1)[0]
    name = re.sub(r"\s+", " ", name).strip(" -(")
    if name.lower().startswith("confidential"):
        return "Confidential"
    return name[:120]


def _usable(url: str) -> bool:
    if not is_direct(url) or is_competitor(url) or is_aggregator(url):
        return False
    host = url.split("/")[2].lower() if "://" in url else ""
    if host.startswith("www."):
        host = host[4:]
    return not any(host == name or host.endswith("." + name) for name in SKIP_HOSTS)


def latest_thread_ids(limit: int = 1) -> list[int]:
    payload = fetch_json(ALGOLIA)
    found = []
    for hit in payload.get("hits") or []:
        title = hit.get("title") or ""
        if not TITLE_RE.match(title):
            continue
        try:
            found.append(int(hit["objectID"]))
        except (KeyError, TypeError, ValueError):
            continue
        if len(found) >= limit:
            break
    return found


def fetch_who_is_hiring(today: date) -> list:
    """Return evidenced jobs from the latest Who is hiring thread."""
    from scraper.sources import _build_job

    thread_ids = latest_thread_ids(limit=1)
    if not thread_ids:
        return []
    story = fetch_json(ITEM.format(thread_ids[0]))
    kids = story.get("kids") or []
    jobs = []
    # The thread is a few hundred comments. Fetch them together.
    from concurrent.futures import ThreadPoolExecutor

    def load(kid: int) -> dict | None:
        try:
            return fetch_json(ITEM.format(kid))
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=12) as pool:
        comments = list(pool.map(load, kids))
    for comment in comments:
        if not comment or comment.get("deleted") or comment.get("dead"):
            continue
        stamp = _unix_stamp(comment.get("time"))
        parsed = parse_comment(comment.get("text") or "", stamp)
        if not parsed:
            continue
        job = _build_job(
            company=parsed["company"],
            position=parsed["position"],
            location_raw=parsed["location"],
            address=None,
            apply_candidates=parsed["links"],
            text=parsed["text"],
            body=parsed["text"],
            posted_at=parsed["posted_at"],
            updated_at=parsed["posted_at"],
            contract="",
            salary=None,
            source=f"hn:{thread_ids[0]}",
            today=today,
        )
        if job:
            jobs.append(job)
    print(f"  hn:whoishiring -> {len(jobs)} evidenced jobs")
    return jobs


def _unix_stamp(value) -> str:
    if not isinstance(value, (int, float)):
        return ""
    moment = datetime.fromtimestamp(float(value), tz=timezone.utc)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")
