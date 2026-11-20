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

EMPLOYMENT_FILTER_OLD = '''
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

EMPLOYMENT_FILTER = '''
  eleventyConfig.addFilter("employmentType", (contract) => {
    const c = String(contract || "").toLowerCase();
    if (c.includes("intern")) return "INTERN";
    if (c.includes("part-time") || c.includes("part time") || c.includes("parttime")) return "PART_TIME";
    if (c.includes("contract") || c.includes("freelance")) return "CONTRACTOR";
    if (c.includes("temp")) return "TEMPORARY";
    return "FULL_TIME";
  });
'''

# The previous publish omitted the field when the ATS had no schedule.
EMPLOYMENT_OPTIONAL = '{% set emp = job.contract | employmentType %}{% if emp %}"employmentType": "{{ emp }}",{% endif %}'
EMPLOYMENT_ALWAYS = '"employmentType": "{{ job.employmentType or (job.contract | employmentType) }}",'

# Already-patched listing pages dropped addressRegion. Put it back, preferring a real region.
INDEX_ADDRESS_OLD = '''"addressLocality": {{ (job.address.addressLocality if job.address else (job.location | extractCity)) | jsonify | safe }}{% set country = job.address.addressCountry if job.address and job.address.addressCountry else (job.location | countryCode) %}{% if country %},
              "addressCountry": "{{ country }}"{% endif %}'''
INDEX_ADDRESS_NEW = '''"addressLocality": {{ (job.address.addressLocality if job.address and job.address.addressLocality else ((job.location | extractCity) or "Remote")) | jsonify | safe }},
              "addressRegion": {{ (job.address.addressRegion if job.address and job.address.addressRegion else (job.address.addressLocality if job.address and job.address.addressLocality else ((job.location | extractCity) or "Remote"))) | jsonify | safe }}{% set country = job.address.addressCountry if job.address and job.address.addressCountry else (job.location | countryCode) %}{% if country %},
              "addressCountry": "{{ country }}"{% endif %}'''

CITY_REGION_OLD = '''"addressLocality": "{{ job.location | extractCity }}",
              "addressRegion": "{{ job.location | extractCity }}",'''
CITY_REGION_NEW = '''"addressLocality": {{ (job.address.addressLocality if job.address and job.address.addressLocality else ((job.location | extractCity) or "Remote")) | jsonify | safe }},
              "addressRegion": {{ (job.address.addressRegion if job.address and job.address.addressRegion else (job.address.addressLocality if job.address and job.address.addressLocality else ((job.location | extractCity) or "Remote"))) | jsonify | safe }},'''

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

TIME_OLD = "{{ job.post_date | timeAgo }}"
TIME_NEW = (
    '{% set postedAt = job.posted_at or job.post_date %}'
    '<time class="js-timeago" datetime="{{ postedAt }}" title="{{ postedAt }}">'
    "{{ postedAt | timeAgo }}</time>"
)

DATE_ATTR_OLD = 'data-date="{{ job.post_date }}"'
DATE_ATTR_NEW = (
    'data-date="{{ job.posted_at or job.post_date }}" '
    'data-country="{{ job.country | lower }}" '
    'data-excerpt="{{ job.excerpt | lower }}"'
)

EXCERPT_HTML = '{% if job.excerpt %}<p class="text-sm text-gray-600 dark:text-gray-400 mb-3">{{ job.excerpt }}</p>{% endif %}'

NOON_OLD = 'dateStr + "T12:00:00"'
NOON_NEW = 'dateStr + "T12:00:00Z"'
NOON_JS_OLD = 'dateString + "T12:00:00"'
NOON_JS_NEW = 'dateString + "T12:00:00Z"'

COUNTRY_LINE_OLD = "const country = parts[parts.length - 1].trim();"
COUNTRY_LINE_NEW = 'const country = (job.country || "").trim() || parts[parts.length - 1].trim();'
# uniqueCountries and groupByCountry loop over job objects. countryCode only
# receives a location string, so the same rewrite makes Eleventy throw
# "job is not defined" and the live board never rebuilds.
COUNTRY_JOB_FILTERS = ("uniqueCountries", "groupByCountry")

SEARCH_OLD = """      var searchable = (card.dataset.position || '') + ' ' +
                       (card.dataset.company || '') + ' ' +
                       (card.dataset.location || '');
      var matchesSearch = !query || tokenMatch(searchable, query);
      var matchesCountry = !country || (card.dataset.location || '').includes(country);"""
SEARCH_NEW = """      var searchable = (card.dataset.position || '') + ' ' +
                       (card.dataset.company || '') + ' ' +
                       (card.dataset.location || '') + ' ' +
                       (card.dataset.excerpt || '');
      var matchesSearch = !query || tokenMatch(searchable, query);
      var matchesCountry = !country || (card.dataset.country || card.dataset.location || '').includes(country);"""

MAIN_JS_TAG = '  <script src="/assets/js/main.js"></script>'
TIMEAGO_TAG = MAIN_JS_TAG + '\n  <script src="/assets/js/timeago.js"></script>'


def _replace_in_filter(text: str, name: str, old: str, new: str) -> str:
    marker = f'addFilter("{name}"'
    start = text.find(marker)
    if start < 0:
        return text
    end = text.find("});", start)
    if end < 0:
        return text
    end += 3
    return text[:start] + text[start:end].replace(old, new) + text[end:]


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
    updated = updated.replace(EMPLOYMENT_FILTER_OLD, EMPLOYMENT_FILTER)
    updated = updated.replace(NOON_OLD, NOON_NEW)
    for name in COUNTRY_JOB_FILTERS:
        updated = _replace_in_filter(updated, name, COUNTRY_LINE_OLD, COUNTRY_LINE_NEW)
    # Repair the publish that applied the job.country rewrite inside countryCode.
    updated = _replace_in_filter(updated, "countryCode", COUNTRY_LINE_NEW, COUNTRY_LINE_OLD)
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
        patched = _patch_jobposting(patched)
        if path.name == "index.njk" and path.parent.name == "src":
            patched = patched.replace(HOME_OLD, HOME_NEW)
        if path.parent.name == "visa-sponsored-jobs" and path.name == "index.njk":
            patched = patched.replace(INDEX_TITLE_OLD, INDEX_TITLE_NEW)
            patched = patched.replace(INDEX_DESC_OLD, INDEX_DESC_NEW)
            patched = _patch_index_schema(patched)
        patched = patch_markup(patched)
        if patched != original:
            path.write_text(patched, encoding="utf-8")
            changed.append(str(path.relative_to(root)))

    main_js = root / "src" / "assets" / "js" / "main.js"
    if main_js.exists():
        current = main_js.read_text(encoding="utf-8")
        fixed = current.replace(NOON_OLD, NOON_NEW).replace(NOON_JS_OLD, NOON_JS_NEW)
        if fixed != current:
            main_js.write_text(fixed, encoding="utf-8")
            changed.append(str(main_js.relative_to(root)))

    base = root / "src" / "_includes" / "layouts" / "base.njk"
    if base.exists():
        current = base.read_text(encoding="utf-8")
        if "timeago.js" not in current and MAIN_JS_TAG in current:
            base.write_text(current.replace(MAIN_JS_TAG, TIMEAGO_TAG, 1), encoding="utf-8")
            changed.append(str(base.relative_to(root)))
    return changed


def _patch_jobposting(text: str) -> str:
    text = text.replace('"employmentType": "FULL_TIME",', EMPLOYMENT_ALWAYS)
    text = text.replace(EMPLOYMENT_OPTIONAL, EMPLOYMENT_ALWAYS)
    text = text.replace(INDEX_ADDRESS_OLD, INDEX_ADDRESS_NEW)
    text = text.replace(CITY_REGION_OLD, CITY_REGION_NEW)
    return text


def patch_markup(text: str) -> str:
    if "js-timeago" not in text:
        text = text.replace(TIME_OLD, TIME_NEW)
    if "data-excerpt" not in text:
        text = text.replace(DATE_ATTR_OLD, DATE_ATTR_NEW)
    if 'class="job-card"' in text and "job.excerpt" not in text:
        text = text.replace(
            '<div class="flex flex-wrap gap-2">',
            EXCERPT_HTML + '\n            <div class="flex flex-wrap gap-2">',
        )
    if "dataset.excerpt" not in text:
        text = text.replace(SEARCH_OLD, SEARCH_NEW)
    text = text.replace(
        '"datePosted": "{{ job.post_date | isoDate }}",',
        '"datePosted": "{{ job.posted_at or (job.post_date | isoDate) }}",',
    )
    return text


def _patch_index_schema(text: str) -> str:
    """Use the stored valid_through and stop emitting an empty street address."""
    text = text.replace(
        '"validThrough": "{{ job.post_date | validThrough }}",',
        '"validThrough": "{{ job.valid_through or (job.post_date | validThrough) }}",',
    )
    text = text.replace(
        '"datePosted": "{{ job.post_date }}",',
        '"datePosted": "{{ job.posted_at or (job.post_date | isoDate) }}",',
    )
    text = text.replace(
        '"datePosted": "{{ job.post_date | isoDate }}",',
        '"datePosted": "{{ job.posted_at or (job.post_date | isoDate) }}",',
    )
    text = text.replace(
        '"title": "{{ job.position }}",',
        '"title": {{ job.position | jsonify | safe }},',
    )
    text = text.replace(
        '"description": "{{ job.position }} at {{ job.company }} — {{ job.location }}. See the employer listing for visa sponsorship and relocation details.",',
        '"description": {{ (job.body or job.summary or (job.position ~ " at " ~ job.company)) | jsonify | safe }},',
    )
    text = text.replace(
        "{{ jobs | length }}+ opportunities with visa sponsorship and relocation assistance",
        "{{ jobs | length }}+ roles with recorded visa-sponsorship evidence",
    )
    text = text.replace(
        '''              "streetAddress": "",
              "addressLocality": "{{ job.location | extractCity }}",
              "addressRegion": "{{ job.location | extractCity }}",
              "postalCode": "",
              "addressCountry": "{{ job.location | countryCode }}"''',
        INDEX_ADDRESS_NEW,
    )
    return _patch_jobposting(text)
