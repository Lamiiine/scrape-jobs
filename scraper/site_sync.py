"""Patch the visajobs.xyz repo so published jobs render with real evidence.

The site repository cannot be pushed to from this agent. ``publish`` applies
these edits on the clone when ``SITE_GITHUB_TOKEN`` is set, then commits them
with the job update.
"""

from __future__ import annotations

from pathlib import Path

OVERLAY = Path(__file__).resolve().parent.parent / "site_overlay"

ELE_OLD_DEFAULT = 'return codes[country] || "EU";'
ELE_NEW_DEFAULT = 'return codes[country] || "";'

ELE_OLD_EUROPE = '"Europe": "EU", '
ELE_NEW_EUROPE = ""

ELE_OLD_WINDOW = "date.setDate(date.getDate() + 90);"
ELE_NEW_WINDOW = "date.setDate(date.getDate() + 45);"

ELE_OLD_FALLBACK = "return new Date(Date.now() + 90 * 86400000).toISOString().split(\"T\")[0];"
ELE_NEW_FALLBACK = "return new Date(Date.now() + 45 * 86400000).toISOString().split(\"T\")[0];"

ELE_COUNTRY_ANCHOR = '"Qatar": "QA",'
ELE_COUNTRY_INSERT = '''"Qatar": "QA",
      "United States": "US", "USA": "US", "US": "US",
      "United States of America": "US",
      "The Netherlands": "NL", "Holland": "NL",
      "Czechia": "CZ", "Luxembourg": "LU", "Estonia": "EE",
      "Lithuania": "LT", "Latvia": "LV", "Hungary": "HU",
      "Croatia": "HR", "Slovakia": "SK", "Slovenia": "SI",
      "Greece": "GR", "Malta": "MT", "Cyprus": "CY", "Iceland": "IS",'''

EMPLOYMENT_FILTER = '''
  eleventyConfig.addFilter("employmentType", (contract) => {
    const c = String(contract || "").toLowerCase();
    if (!c) return "";
    if (c.includes("intern")) return "INTERN";
    if (c.includes("part")) return "PART_TIME";
    if (c.includes("contract") || c.includes("freelance")) return "CONTRACTOR";
    if (c.includes("temp")) return "TEMPORARY";
    if (c.includes("full")) return "FULL_TIME";
    return "";
  });
'''

CONTRACT_BADGE = '<span class="badge badge-contract">{{ job.contract }}</span>'
CONTRACT_BADGE_SAFE = '{% if job.contract %}<span class="badge badge-contract">{{ job.contract }}</span>{% endif %}'

HOME_OLD = '''        <div class="text-3xl font-bold text-gray-900 dark:text-white mb-1">100%</div>
        <div class="text-gray-600 dark:text-gray-400 text-sm">Visa Sponsored</div>'''
HOME_NEW = '''        <div class="text-3xl font-bold text-gray-900 dark:text-white mb-1">Checked</div>
        <div class="text-gray-600 dark:text-gray-400 text-sm">Sponsorship evidence</div>'''

INDEX_TITLE_OLD = 'title: "Visa Sponsorship Jobs in Europe & Worldwide — 270+ Open Roles (2026)"'
INDEX_TITLE_NEW = 'title: "Visa Sponsorship Jobs"'
INDEX_DESC_OLD = 'description: "Browse 270+ verified tech jobs with visa sponsorship and relocation assistance. Companies like Stripe, Revolut, Cloudflare, and Spotify are hiring now. Updated weekly."'
INDEX_DESC_NEW = 'description: "Tech jobs whose postings or a known sponsor list show visa sponsorship. Relocation assistance is listed only when the posting says so."'


def patch_eleventy(text: str) -> str:
    updated = text.replace(ELE_OLD_DEFAULT, ELE_NEW_DEFAULT)
    updated = updated.replace(ELE_OLD_EUROPE, ELE_NEW_EUROPE)
    updated = updated.replace(ELE_OLD_WINDOW, ELE_NEW_WINDOW)
    updated = updated.replace(ELE_OLD_FALLBACK, ELE_NEW_FALLBACK)
    if '"United States": "US"' not in updated and ELE_COUNTRY_ANCHOR in updated:
        updated = updated.replace(ELE_COUNTRY_ANCHOR, ELE_COUNTRY_INSERT, 1)
    if 'addFilter("employmentType"' not in updated:
        needle = 'eleventyConfig.addFilter("limit"'
        if needle in updated:
            updated = updated.replace(needle, EMPLOYMENT_FILTER + "\n  " + needle, 1)
    return updated


def patch_tree(root: Path) -> list[str]:
    """Apply overlay files and in-place template fixes. Returns changed paths."""
    changed: list[str] = []
    if OVERLAY.is_dir():
        for source in OVERLAY.rglob("*"):
            if not source.is_file():
                continue
            relative = source.relative_to(OVERLAY)
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            data = source.read_text(encoding="utf-8")
            previous = target.read_text(encoding="utf-8") if target.exists() else None
            if previous != data:
                target.write_text(data, encoding="utf-8")
                changed.append(str(relative))

    eleventy = root / ".eleventy.js"
    if eleventy.exists():
        original = eleventy.read_text(encoding="utf-8")
        patched = patch_eleventy(original)
        if patched != original:
            eleventy.write_text(patched, encoding="utf-8")
            changed.append(".eleventy.js")

    for path in (root / "src").rglob("*.njk") if (root / "src").exists() else []:
        original = path.read_text(encoding="utf-8")
        patched = original.replace(CONTRACT_BADGE, CONTRACT_BADGE_SAFE)
        patched = patched.replace(
            '"validThrough": "{{ job.post_date | validThrough }}",',
            '"validThrough": "{{ job.valid_through or (job.post_date | validThrough) }}",',
        )
        patched = patched.replace(
            '"employmentType": "FULL_TIME",',
            '{% set emp = job.contract | employmentType %}{% if emp %}"employmentType": "{{ emp }}",{% endif %}',
        )
        if path.name == "index.njk" and path.parent.name == "src":
            patched = patched.replace(HOME_OLD, HOME_NEW)
        if path.parent.name == "visa-sponsored-jobs" and path.name == "index.njk":
            patched = patched.replace(INDEX_TITLE_OLD, INDEX_TITLE_NEW)
            patched = patched.replace(INDEX_DESC_OLD, INDEX_DESC_NEW)
            patched = _patch_index_schema(patched)
        if patched != original:
            path.write_text(patched, encoding="utf-8")
            changed.append(str(path.relative_to(root)))
    return changed


def _patch_index_schema(text: str) -> str:
    """Use the stored valid_through and stop emitting an empty street address."""
    text = text.replace(
        '"validThrough": "{{ job.post_date | validThrough }}",',
        '"validThrough": "{{ job.valid_through or (job.post_date | validThrough) }}",',
    )
    text = text.replace(
        '"datePosted": "{{ job.post_date }}",',
        '"datePosted": "{{ job.post_date | isoDate }}",',
    )
    text = text.replace(
        '"title": "{{ job.position }}",',
        '"title": {{ job.position | jsonify | safe }},',
    )
    text = text.replace(
        '"description": "{{ job.position }} at {{ job.company }} — {{ job.location }}. See the employer listing for visa sponsorship and relocation details.",',
        '"description": {{ (job.summary or (job.position ~ " at " ~ job.company)) | jsonify | safe }},',
    )
    text = text.replace(
        "{{ jobs | length }}+ opportunities with visa sponsorship and relocation assistance",
        "{{ jobs | length }}+ roles with recorded visa-sponsorship evidence",
    )
    text = text.replace(
        '"employmentType": "FULL_TIME",',
        '{% set emp = job.contract | employmentType %}{% if emp %}"employmentType": "{{ emp }}",{% endif %}',
    )
    text = text.replace(
        '''              "streetAddress": "",
              "addressLocality": "{{ job.location | extractCity }}",
              "addressRegion": "{{ job.location | extractCity }}",
              "postalCode": "",
              "addressCountry": "{{ job.location | countryCode }}"''',
        '''              "addressLocality": {{ (job.address.addressLocality if job.address else (job.location | extractCity)) | jsonify | safe }}{% set country = job.address.addressCountry if job.address and job.address.addressCountry else (job.location | countryCode) %}{% if country %},
              "addressCountry": "{{ country }}"{% endif %}''',
    )
    return text
