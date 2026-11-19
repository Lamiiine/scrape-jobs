"""Match the Eleventy ``jobSlug`` filter so social posts link to the live page."""

from __future__ import annotations

import re

from scraper.models import Job


def job_slug(job: Job) -> str:
    base = f"{job.company}-{job.position}-{job.location or ''}"
    base = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")[:80]
    digest = _js_hash(job.apply_url or "")
    return f"{base}-{_base36(digest)[:4]}"


def job_page(job: Job) -> str:
    return f"https://visajobs.xyz/visa-sponsored-jobs/{job_slug(job)}/"


def _js_hash(value: str) -> int:
    hashed = 0
    for char in value:
        hashed = ((hashed << 5) - hashed + ord(char)) & 0xFFFFFFFF
        if hashed & 0x80000000:
            hashed -= 0x100000000
    return abs(hashed)


def _base36(number: int) -> str:
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    if number == 0:
        return "0"
    chars = []
    while number:
        number, remainder = divmod(number, 36)
        chars.append(digits[remainder])
    return "".join(reversed(chars))
