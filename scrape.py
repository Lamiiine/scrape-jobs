#!/usr/bin/env python3
"""Daily visa-sponsorship scraper.

Writes data/latest-jobs.json and, when SITE_GITHUB_TOKEN is set, updates
relocate-with-us/relocate-with-us.github.io (new jobs, expired jobs, templates).
"""

from __future__ import annotations

import argparse
import json
import sys

from scraper.pipeline import DATA_PATH, scrape, write_outputs
from scraper.publish import publish_jobs
from scraper.social import announce
from scraper.urls import canonical_url


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scrape evidenced visa-sponsorship jobs")
    parser.add_argument("--skip-live", action="store_true", help="Skip HTTP checks of apply URLs")
    parser.add_argument("--no-publish", action="store_true", help="Do not try to update the site repo")
    parser.add_argument("--no-announce", action="store_true", help="Do not post to Telegram or LinkedIn")
    parser.add_argument("--dry-run", action="store_true", help="Scrape and print counts only")
    args = parser.parse_args(argv)

    already = _known_urls()
    jobs, errors = scrape(skip_live=args.skip_live)
    print(f"Source errors: {len(errors)}")
    for error in errors:
        print(f"  {error}")
    if not jobs:
        print("No evidenced jobs. Refusing to update catalogs.")
        return 1
    fresh = [job for job in jobs if canonical_url(job.apply_url) not in already]
    print(f"New since the last catalog: {len(fresh)}")
    if args.dry_run:
        return 0
    write_outputs(jobs)
    if not args.no_announce:
        announce(fresh)
    if args.no_publish:
        return 0
    publish_jobs(jobs)
    return 0


def _known_urls() -> set[str]:
    if not DATA_PATH.exists():
        return set()
    try:
        rows = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    return {
        canonical_url(row.get("apply_url") or row.get("description") or "")
        for row in rows
        if isinstance(row, dict)
    }


if __name__ == "__main__":
    sys.exit(main())
