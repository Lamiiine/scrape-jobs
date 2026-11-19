"""The daily Telegram and LinkedIn post.

Edit the strings in this file to change how the digest looks. The rest of the
scraper only fills the placeholders. Telegram uses HTML so the apply link is
the words "View & apply" and the address itself stays hidden. LinkedIn has no
hidden links, so the same words are followed by the page address.
"""

from __future__ import annotations

from datetime import date
from html import escape

from scraper.locations import parse_location
from scraper.models import Job
from scraper.slug import job_page

# --- copy. keep the placeholders, change the wording around them. ---

VISA_CONFIRMED = "✅ Visa sponsorship confirmed"
VISA_LIKELY = "Visa sponsorship likely"
RELOCATION = "✈️ Relocation support"

TELEGRAM_HEADER = "<b>Visa-sponsored roles</b>\n{date}"
TELEGRAM_ROLE = (
    "{flag} <b>{title}</b>\n"
    "{company} · {place}\n"
    "{salary_line}"
    "{visa_line}\n"
    "{relocation_line}"
    '<a href="{page}">View &amp; apply</a>'
)
TELEGRAM_FOOTER = (
    '<a href="https://visajobs.xyz/visa-sponsored-jobs/">visajobs.xyz/visa-sponsored-jobs</a>\n'
    "Share with a friend who wants to move abroad."
)

LINKEDIN_HEADER = "Visa-sponsored roles\n{date}"
LINKEDIN_ROLE = (
    "{flag} {title}\n"
    "{company} · {place}\n"
    "{salary_line}"
    "{visa_line}\n"
    "{relocation_line}"
    "View & apply: {page}"
)
LINKEDIN_FOOTER = (
    "visajobs.xyz/visa-sponsored-jobs\n"
    "Share with a friend who wants to move abroad."
)
LINKEDIN_HASHTAGS = "#visasponsorship #relocation #techjobs #hiring"

BOARD_URL = "https://visajobs.xyz/visa-sponsored-jobs/"
_SYMBOLS = {"EUR": "€", "GBP": "£", "USD": "$"}


def render_telegram(jobs: list[Job], on: date) -> str:
    blocks = [_role_html(job) for job in jobs]
    body = TELEGRAM_HEADER.format(date=escape(_day(on)))
    if blocks:
        body = body + "\n\n" + "\n\n".join(blocks)
    return body + "\n\n" + TELEGRAM_FOOTER


def render_telegram_preview(jobs: list[Job], on: date) -> str:
    """What a reader sees in Telegram, without the HTML tags."""
    return _visible(render_telegram(jobs, on))


def render_linkedin(jobs: list[Job], on: date) -> str:
    blocks = [_role_plain(job) for job in jobs]
    body = LINKEDIN_HEADER.format(date=_day(on))
    if blocks:
        body = body + "\n\n" + "\n\n".join(blocks)
    return body + "\n\n" + LINKEDIN_FOOTER + "\n\n" + LINKEDIN_HASHTAGS


def _day(on: date) -> str:
    return on.strftime("%a %d %b").replace(" 0", " ")


def _role_html(job: Job) -> str:
    fields = _fields(job)
    return TELEGRAM_ROLE.format(
        flag=fields["flag"],
        title=escape(fields["title"]),
        company=escape(fields["company"]),
        place=escape(fields["place"]),
        salary_line=(escape(fields["salary"]) + "\n") if fields["salary"] else "",
        visa_line=escape(fields["visa"]),
        relocation_line=(RELOCATION + "\n") if fields["relocation"] else "",
        page=escape(fields["page"], quote=True),
    )


def _role_plain(job: Job) -> str:
    fields = _fields(job)
    return LINKEDIN_ROLE.format(
        flag=fields["flag"],
        title=fields["title"],
        company=fields["company"],
        place=fields["place"],
        salary_line=(fields["salary"] + "\n") if fields["salary"] else "",
        visa_line=fields["visa"],
        relocation_line=(RELOCATION + "\n") if fields["relocation"] else "",
        page=fields["page"],
    )


def _fields(job: Job) -> dict[str, str | bool]:
    place, code = _place(job)
    level = job.sponsorship_evidence
    if level == "confirmed":
        visa = VISA_CONFIRMED
    elif level == "likely":
        visa = VISA_LIKELY
    else:
        visa = ""
    return {
        "flag": _flag(code),
        "title": job.position or "Open role",
        "company": job.company or "Company",
        "place": place,
        "salary": _salary(job.salary),
        "visa": visa,
        "relocation": bool(job.reloc),
        "page": job_page(job),
    }


def _place(job: Job) -> tuple[str, str]:
    parsed = parse_location(job.location or "", job.address or None)
    city = parsed.locality
    country = parsed.country or job.country or ""
    code = parsed.country_code or ""
    if city and country and city.lower() != country.lower():
        return f"{city}, {country}", code
    if country:
        return country, code
    if city:
        return city, code
    return job.location or "Location to be confirmed", code


def _flag(code: str) -> str:
    code = (code or "").strip().upper()
    if len(code) != 2 or not code.isalpha():
        return "🌍"
    return chr(0x1F1E6 + ord(code[0]) - 65) + chr(0x1F1E6 + ord(code[1]) - 65)


def _salary(salary: dict | None) -> str:
    if not salary:
        return ""
    try:
        minimum = int(salary.get("min"))
    except (TypeError, ValueError):
        return ""
    maximum = salary.get("max")
    try:
        maximum = int(maximum) if maximum not in (None, "") else None
    except (TypeError, ValueError):
        maximum = None
    code = str(salary.get("currency") or "").upper()
    prefix = _SYMBOLS.get(code, f"{code} " if code else "")
    rounded = _round_thousands(minimum) and (maximum is None or _round_thousands(maximum))
    text = _amount(minimum, prefix, rounded)
    if maximum and maximum != minimum:
        text = f"{text}–{_amount(maximum, prefix, rounded)}"
    unit = str(salary.get("unit") or "YEAR").upper()
    if unit == "HOUR":
        text += " an hour"
    return text


def _round_thousands(value: int) -> bool:
    return value >= 10000 and value % 1000 == 0


def _amount(value: int, prefix: str, rounded: bool) -> str:
    if rounded:
        return f"{prefix}{value // 1000}k"
    return f"{prefix}{value:,}"


def _visible(html: str) -> str:
    import re

    text = re.sub(r"<a\s+href=\"[^\"]*\">", "", html, flags=re.I)
    text = re.sub(r"</a>", "", text, flags=re.I)
    text = re.sub(r"</?b>", "", text, flags=re.I)
    return (
        text.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
    )
