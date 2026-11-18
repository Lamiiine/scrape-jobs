"""Check that an apply URL still resolves to a live posting."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper.http_util import fetch

DEAD_MARKERS = (
    "no longer active",
    "no longer available",
    "job posting has been removed",
    "posting has been removed",
    "stelle nicht mehr verfügbar",
    "this job has expired",
    "page_not_found_404",
)


def check_url(url: str, timeout: float = 12) -> str:
    """Return alive, dead, or inconclusive."""
    status, body, final = fetch(url, timeout=timeout, read_limit=4096)
    final_l = (final or "").lower()
    snippet = body.decode("utf-8", "ignore").lower()
    if status in (404, 410, 451):
        return "dead"
    if "not_found=true" in final_l:
        return "dead"
    if "error=true" in final_l and "greenhouse" in final_l:
        return "dead"
    if any(marker in snippet for marker in DEAD_MARKERS):
        return "dead"
    if 200 <= status < 400:
        return "alive"
    return "inconclusive"


def check_many(urls: list[str], workers: int = 12) -> dict[str, str]:
    results: dict[str, str] = {}
    if not urls:
        return results
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(check_url, url): url for url in urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                results[url] = future.result()
            except Exception:
                results[url] = "inconclusive"
    return results
