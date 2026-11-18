"""Dedupe, cap, and expire listings before they are written to the site."""

from __future__ import annotations

from datetime import date

from scraper.models import WINDOW_DAYS, Job, parse_iso
from scraper.urls import canonical_url, is_competitor

# Keeps the static jobs index from growing back into a 1 MB document,
# and stops one employer's boilerplate from filling the board.
MAX_BOARD = 350
MAX_PER_COMPANY = 40
# Refuse to replace the live board when a scrape clearly failed.
MIN_PUBLISH = 40


def dedupe(jobs: list[Job]) -> list[Job]:
    """Keep one row per apply URL and per company + title + country.

    Confirmed evidence wins over likely, then the newer posting wins.
    """
    seen: set[str] = set()
    kept: list[Job] = []
    ranked = sorted(
        jobs,
        key=lambda job: (
            0 if job.sponsorship_evidence == "confirmed" else 1,
            _invert_date(job.post_date),
        ),
    )
    for job in ranked:
        url = canonical_url(job.apply_url)
        title_key = f"{job.company.strip().lower()}|{job.position.strip().lower()}|{job.address.get('addressCountry', '')}"
        if not url or url in seen or title_key in seen:
            continue
        seen.add(url)
        seen.add(title_key)
        kept.append(job)
    return kept


def _invert_date(value: str) -> str:
    # ISO dates sort lexicographically; a leading flag already groups evidence.
    # Negate by swapping digits so newer dates come first inside the sorted() order.
    return "".join(chr(ord("9") - (ord(ch) - ord("0"))) if ch.isdigit() else ch for ch in value)


def select_board(jobs: list[Job], limit: int = MAX_BOARD, per_company: int = MAX_PER_COMPANY) -> list[Job]:
    unique = dedupe(jobs)
    unique.sort(key=lambda job: job.post_date, reverse=True)
    confirmed = [job for job in unique if job.sponsorship_evidence == "confirmed"]
    likely = [job for job in unique if job.sponsorship_evidence == "likely"]
    chosen: list[Job] = []
    counts: dict[str, int] = {}
    for job in confirmed + likely:
        key = job.company.strip().lower()
        if counts.get(key, 0) >= per_company:
            continue
        counts[key] = counts.get(key, 0) + 1
        chosen.append(job)
        if len(chosen) >= limit:
            break
    chosen.sort(key=lambda job: job.post_date, reverse=True)
    return chosen


def job_from_site(record: dict) -> dict:
    return record


def expire_and_merge(existing: list[dict], fresh: list[Job], today: date) -> dict:
    """Replace the site catalog with today's capped board.

    Existing rows without ``sponsorship_evidence`` were blanket-tagged by the
    old fetcher. They are removed. A previously published job stays only when
    today's scrape still selects it, so the per-company cap cannot drift as
    older postings remain inside their ``valid_through`` window.
    """
    desired_jobs = select_board(fresh)
    desired = [job.to_site() for job in desired_jobs]
    desired_urls = {canonical_url(row["apply_url"]): row for row in desired}
    existing_urls: set[str] = set()
    removed: list[dict] = []

    for record in existing:
        url = canonical_url(record.get("apply_url") or record.get("description") or "")
        if url in desired_urls:
            existing_urls.add(url)
            continue
        evidence = (record.get("sponsorship_evidence") or "").strip()
        if not url or not str(record.get("description") or record.get("apply_url") or "").startswith("http"):
            reason = "missing-url"
        elif is_competitor(url):
            reason = "competitor-board"
        elif evidence not in ("confirmed", "likely"):
            reason = "no-evidence"
        elif record.get("link_status") == "dead":
            reason = "dead-link"
        else:
            through = parse_iso(record.get("valid_through") or "")
            posted = parse_iso(record.get("post_date") or "")
            if through is None and posted is not None:
                through = date.fromordinal(posted.toordinal() + WINDOW_DAYS)
            reason = "expired" if through is not None and through < today else "not-in-latest-board"
        removed.append({
            "company": record.get("company", ""),
            "position": record.get("position", ""),
            "url": url,
            "reason": reason,
        })

    added = [row for url, row in desired_urls.items() if url not in existing_urls]
    return {
        "jobs": desired,
        "added": added,
        "removed": removed,
    }
