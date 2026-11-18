"""Push evidenced jobs to relocate-with-us/relocate-with-us.github.io and drop stale rows."""

from __future__ import annotations

import base64
import json
import os
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path

from scraper.catalog import MIN_PUBLISH, expire_and_merge
from scraper.models import Job
from scraper.site_sync import patch_tree

DEFAULT_REPO = "relocate-with-us/relocate-with-us.github.io"

OWNER_MESSAGE = """
OWNER ACTION REQUIRED
The scraper ran, but it cannot update visajobs.xyz until a secret is added.

1. Create a GitHub personal access token for an account that can push to
   relocate-with-us/relocate-with-us.github.io.
   Fine-grained token:
     - Repository access: only relocate-with-us/relocate-with-us.github.io
     - Contents: Read and write
     - Actions: Read and write
     - Metadata: Read
   A classic PAT with repo scope also works. Do not use scrape-jobs' GITHUB_TOKEN;
   that token cannot push to the other repository.
2. In Lamiiine/scrape-jobs → Settings → Secrets and variables → Actions,
   create a repository secret named SITE_GITHUB_TOKEN with that token.
3. Run the "Daily Job Scraper" workflow with "Run workflow".

Why this is required: the site workflow "Fetch & Add Visa Jobs" commits with
GITHUB_TOKEN. GitHub does not start the "Build and Deploy" workflow on those
pushes, and the follow-up `gh workflow run deploy.yml` returns HTTP 403 because
that workflow only has contents: write. The public site has therefore stayed on
the 13 August 2026 deploy. A push made with SITE_GITHUB_TOKEN is a normal push
and does trigger Build and Deploy.

No Gemini API key is required. The old fetcher called Gemini once per job,
hit HTTP 429, and published about one job a day.
""".strip()


def _run(cmd: list[str], cwd: Path, env: dict | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, env=env)


def publish_jobs(jobs: list[Job], today: date | None = None, repo: str | None = None, token: str | None = None, workdir: Path | None = None) -> dict:
    today = today or datetime.now(timezone.utc).date()
    token = token if token is not None else os.environ.get("SITE_GITHUB_TOKEN", "")
    repo = repo or os.environ.get("SITE_REPO", DEFAULT_REPO)
    if not token:
        print(OWNER_MESSAGE)
        return {"published": False, "reason": "missing-token", "fresh": len(jobs)}
    if len(jobs) < MIN_PUBLISH:
        print(
            f"Refusing to publish {len(jobs)} jobs (minimum {MIN_PUBLISH}). "
            "The live catalog was left unchanged so a failed scrape cannot wipe it."
        )
        return {"published": False, "reason": "too-few-jobs", "fresh": len(jobs)}

    root = workdir or Path("/tmp/visajobs-site")
    if root.exists():
        subprocess.run(["rm", "-rf", str(root)], check=True)
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    # Clone the public URL. The token is attached only as an HTTP header so it
    # does not appear in the remote URL if git prints an error.
    _run(["git", "clone", "--depth", "1", f"https://github.com/{repo}.git", str(root)], cwd=Path("/tmp"), env=env)
    basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    _run(
        ["git", "config", "http.https://github.com/.extraheader", f"AUTHORIZATION: basic {basic}"],
        cwd=root,
    )

    jobs_path = root / "src" / "_data" / "jobs.json"
    existing = json.loads(jobs_path.read_text(encoding="utf-8")) if jobs_path.exists() else []
    merged = expire_and_merge(existing, jobs, today)
    payload = json.dumps(merged["jobs"], indent=2, ensure_ascii=False) + "\n"
    jobs_path.parent.mkdir(parents=True, exist_ok=True)
    jobs_path.write_text(payload, encoding="utf-8")
    (root / "db.json").write_text(payload, encoding="utf-8")

    removed = merged["removed"]
    log_path = root / "scripts" / "removed-jobs.log"
    if removed:
        lines = [
            f"[{datetime.now(timezone.utc).isoformat()}] REMOVED: {row['company']} | {row['position']} | {row['url']} | {row['reason']}"
            for row in removed
        ]
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")

    added_log = root / "scripts" / "added-jobs.log"
    if merged["added"]:
        lines = [
            f"[{datetime.now(timezone.utc).isoformat()}] ADDED: {row['company']} | {row['position']} | {row['location']} | {row['sponsorship_evidence']} | {row['description']}"
            for row in merged["added"]
        ]
        with added_log.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")

    changed_files = patch_tree(root)
    _run(["git", "config", "user.name", "github-actions[bot]"], cwd=root)
    _run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], cwd=root)
    _run(["git", "add", "-A"], cwd=root)
    status = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=root)
    if status.returncode == 0:
        print("Site repository already matches this scrape. Nothing to push.")
        return {"published": False, "reason": "no-changes", "added": 0, "removed": len(removed)}

    stamp = today.strftime("%B %-d, %Y")
    added_n = len(merged["added"])
    removed_n = len(removed)
    message = f"feat(jobs): add {added_n} visa-sponsored jobs ({stamp})"
    if removed_n:
        message += f"\n\nRemoved {removed_n} stale, competitor, or unevidenced listings."
    if changed_files:
        message += "\n\nUpdated job templates so sponsorship claims follow sponsorship_evidence."
    _run(["git", "commit", "-m", message], cwd=root)
    _run(["git", "push", "origin", "HEAD:main"], cwd=root)
    print(f"Pushed {added_n} new jobs and removed {removed_n} listings to {repo}.")
    print("That push should start Build and Deploy, because it is not made with the site's GITHUB_TOKEN.")
    return {
        "published": True,
        "added": added_n,
        "removed": removed_n,
        "live": len(merged["jobs"]),
        "templates": changed_files,
    }
