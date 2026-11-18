#!/usr/bin/env python3
"""Daily visa-sponsorship scraper.

Writes data/latest-jobs.json and, when SITE_GITHUB_TOKEN is set, updates
relocate-with-us/relocate-with-us.github.io (new jobs, expired jobs, templates).
"""

from __future__ import annotations

import argparse
import sys

from scraper.pipeline import scrape, write_outputs
from scraper.publish import publish_jobs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scrape evidenced visa-sponsorship jobs")
    parser.add_argument("--skip-live", action="store_true", help="Skip HTTP checks of apply URLs")
    parser.add_argument("--no-publish", action="store_true", help="Do not try to update the site repo")
    parser.add_argument("--dry-run", action="store_true", help="Scrape and print counts only")
    args = parser.parse_args(argv)

    jobs, errors = scrape(skip_live=args.skip_live)
    print(f"Source errors: {len(errors)}")
    for error in errors:
        print(f"  {error}")
    if not jobs:
        print("No evidenced jobs. Refusing to update catalogs.")
        return 1
    if args.dry_run:
        return 0
    write_outputs(jobs)
    if args.no_publish:
        return 0
    publish_jobs(jobs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
