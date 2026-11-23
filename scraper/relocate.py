"""Read public relocate.me job pages and keep the employer's own apply link.

relocate.me's robots file allows the public job pages and the job sitemap.
Their /api/ path is disallowed, so this source does not call it. Jaabz is not
fetched: their terms forbid scraping.
"""

from __future__ import annotations

import json
import re
from datetime import date
from html import unescape

from scraper.http_util import fetch
from scraper.urls import is_competitor, is_direct

SITEMAP = "https://relocate.me/sitemap-jobs.xml"
MAX_PAGES = 40

_URL_BLOCK = re.compile(r"<url>(.*?)</url>", re.S)
_LOC = re.compile(r"<loc>([^<]+)</loc>")
_MOD = re.compile(r"<lastmod>([^<]+)</lastmod>")
_JSONLD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
_APPLY = re.compile(
    r'<a\s+href="([^"]+)"[^>]*class="job-apply__button"',
    re.I,
)
_PACKAGE = re.compile(r'class="job-package".*?</section>', re.S)
_PACKAGE_ITEM = re.compile(r"<span>([^<]{2,80})</span>")

_CONTRACTS = {
    "FULL_TIME": "Full-time",
    "PART_TIME": "Part-time",
    "CONTRACTOR": "Contract",
    "INTERN": "Internship",
    "TEMPORARY": "Temporary",
}


def fetch_relocate(today: date) -> list:
    status, body, _final = fetch(SITEMAP, timeout=30)
    if status != 200:
        raise RuntimeError(f"sitemap HTTP {status}")
    pages = parse_sitemap(body.decode("utf-8", "replace"))
    jobs = []
    for url, _modified in pages[:MAX_PAGES]:
        try:
            page_status, page, _page_url = fetch(url, timeout=30)
        except Exception as exc:
            print(f"  relocate.me skip {url}: {exc}")
            continue
        if page_status != 200:
            print(f"  relocate.me skip {url}: HTTP {page_status}")
            continue
        job = job_from_page(page.decode("utf-8", "replace"), today)
        if job:
            jobs.append(job)
    print(f"  relocate.me -> {len(jobs)} evidenced jobs")
    return jobs


def parse_sitemap(xml: str) -> list[tuple[str, str]]:
    found = []
    for block in _URL_BLOCK.findall(xml):
        loc = _LOC.search(block)
        if not loc:
            continue
        modified = _MOD.search(block)
        found.append((unescape(loc.group(1).strip()), modified.group(1).strip() if modified else ""))
    return found


def job_from_page(html: str, today: date):
    from scraper.sources import _build_job, _iso_stamp

    posting = _jobposting(html)
    if not posting:
        return None
    title = str(posting.get("title") or "").strip()
    if not title or "curated" in title.lower():
        return None
    org = posting.get("hiringOrganization") or {}
    company = str(org.get("name") or "").strip() if isinstance(org, dict) else ""
    if company.lower() in {"the global move", "relocate.me"}:
        return None
    apply_url = _apply_url(html)
    if not apply_url or not is_direct(apply_url) or is_competitor(apply_url):
        return None
    address = {}
    place = posting.get("jobLocation") or {}
    if isinstance(place, dict):
        raw_address = place.get("address") or {}
        if isinstance(raw_address, dict):
            address = raw_address
    city = str(address.get("addressLocality") or "").strip()
    country = str(address.get("addressCountry") or "").strip()
    if isinstance(country, dict):
        country = str(country.get("name") or "")
    location = ", ".join(part for part in (city, country) if part) or "Remote"
    package = _package(html)
    description = str(posting.get("description") or "")
    extra = "Relocation package includes:\n" + "\n".join(package) if package else ""
    text = "\n".join(part for part in (title, extra, description) if part)
    posted = _iso_stamp(posting.get("datePosted") or "")
    contract = _CONTRACTS.get(str(posting.get("employmentType") or "").upper(), "")
    return _build_job(
        company=company,
        position=title,
        location_raw=location,
        address=None,
        apply_candidates=[apply_url],
        text=text,
        body=text,
        posted_at=posted,
        updated_at=posted,
        contract=contract,
        salary=None,
        source="relocate.me",
        today=today,
    )


def _jobposting(html: str) -> dict | None:
    for raw in _JSONLD.findall(html):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@type") == "JobPosting":
            return data
    return None


def _apply_url(html: str) -> str:
    match = _APPLY.search(html)
    if not match:
        return ""
    return unescape(match.group(1)).strip()


def _package(html: str) -> list[str]:
    section = _PACKAGE.search(html)
    chunk = section.group(0) if section else html
    found = []
    for item in _PACKAGE_ITEM.findall(chunk):
        text = unescape(item).strip()
        if text and text not in found:
            found.append(text)
    return found
