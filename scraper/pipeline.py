"""Scrape, check links, and write the local catalog."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from scraper.catalog import select_board
from scraper.liveness import check_many
from scraper.models import Job
from scraper.sources import fetch_all

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "latest-jobs.json"
README_PATH = ROOT / "README.md"
START = "<!-- START OF JOB LISTINGS -->"
END = "<!-- END OF JOB LISTINGS -->"


def scrape(skip_live: bool = False) -> tuple[list[Job], list[str]]:
    print("Fetching employer ATS boards...")
    jobs, errors = fetch_all()
    print(f"Evidenced jobs before link checks: {len(jobs)}")
    if not skip_live and jobs:
        print(f"Checking {len(jobs)} apply links...")
        statuses = check_many([job.apply_url for job in jobs])
        alive = []
        dead = 0
        for job in jobs:
            status = statuses.get(job.apply_url, "inconclusive")
            if status == "dead":
                dead += 1
                continue
            if status == "alive":
                job.link_status = "alive"
            alive.append(job)
        print(f"Dropped {dead} dead apply links; {len(alive)} remain")
        jobs = alive
    board = select_board(jobs)
    counts = _counts(board)
    print(
        f"Board: {len(board)} jobs "
        f"({counts['confirmed']} confirmed, {counts['likely']} likely, "
        f"{counts['with_salary']} with salary, {counts['with_relocation']} with relocation)"
    )
    return board, errors


def write_outputs(jobs: list[Job]) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = [job.to_local() for job in jobs]
    DATA_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_readme(jobs)


def _counts(jobs: list[Job]) -> dict[str, int]:
    return {
        "confirmed": sum(1 for job in jobs if job.sponsorship_evidence == "confirmed"),
        "likely": sum(1 for job in jobs if job.sponsorship_evidence == "likely"),
        "with_salary": sum(1 for job in jobs if job.salary),
        "with_relocation": sum(1 for job in jobs if job.reloc),
    }


def _write_readme(jobs: list[Job]) -> None:
    counts = _counts(jobs)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        START,
        "# Visa sponsorship jobs",
        "",
        f"Updated on {now}",
        "",
        f"- Listings: **{len(jobs)}**",
        f"- Sponsorship evidence confirmed: **{counts['confirmed']}**",
        f"- Sponsorship evidence likely (known sponsor list): **{counts['likely']}**",
        f"- With a salary range: **{counts['with_salary']}**",
        f"- With relocation assistance in the posting: **{counts['with_relocation']}**",
        "",
        "Only jobs with `sponsorship_evidence` of `confirmed` or `likely` are included.",
        "Apply links are employer or ATS URLs. Competitor boards are not used.",
        "",
        "| Title | Company | Location | Evidence | Valid through | Apply |",
        "|-------|---------|----------|----------|---------------|-------|",
    ]
    for job in jobs[:40]:
        title = job.position.replace("|", "/")
        company = job.company.replace("|", "/")
        location = job.location.replace("|", "/")
        lines.append(
            f"| {title} | {company} | {location} | {job.sponsorship_evidence} | {job.valid_through} | [Apply]({job.apply_url}) |"
        )
    if len(jobs) > 40:
        lines.append("")
        lines.append(f"_Showing 40 of {len(jobs)}. The full catalog is `data/latest-jobs.json`._")
    lines.append(END)
    section = "\n".join(lines) + "\n"
    existing = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
    start = existing.find(START)
    end = existing.find(END)
    if start != -1 and end != -1:
        updated = existing[:start] + section + existing[end + len(END):]
    else:
        updated = (existing.rstrip() + "\n\n" if existing else "") + section
    README_PATH.write_text(updated, encoding="utf-8")
