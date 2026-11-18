"""Fetch openings from employer ATS APIs and keep the ones with sponsorship evidence."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from html import unescape

from scraper.boards import BOARDS, KNOWN_SPONSOR_KEYS
from scraper.classify import classify, html_to_text, opening_excerpt, strip_html
from scraper.http_util import fetch_json
from scraper.locations import parse_location
from scraper.models import Job, valid_through, visa_label
from scraper.salary import parse_salary, salary_from_numbers
from scraper.urls import canonical_url, choose_apply_url, is_competitor, is_direct

def _iso_stamp(value) -> str:
    """UTC timestamp ``YYYY-MM-DDTHH:MM:SSZ``. Empty when the board has no time.

    A date with no clock is not invented as "now". Callers that only have a
    calendar day get noon UTC, which the site can still tell apart from a
    real posting instant because the source boards send offsets.
    """
    if value is None or value == "":
        return ""
    if isinstance(value, (int, float)):
        stamp = float(value)
        if stamp > 10_000_000_000:
            stamp /= 1000
        moment = datetime.fromtimestamp(stamp, tz=timezone.utc)
        return moment.strftime("%Y-%m-%dT%H:%M:%SZ")
    text = str(value).strip()
    if not text:
        return ""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return text + "T12:00:00Z"
    try:
        moment = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return ""
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _iso_date(value) -> date | None:
    stamp = _iso_stamp(value)
    if not stamp:
        return None
    try:
        return date.fromisoformat(stamp[:10])
    except ValueError:
        return None


def _contract_from_text(*chunks: str) -> str:
    blob = " ".join(c for c in chunks if c).lower()
    if re.search(r"\bintern(ship)?\b", blob):
        return "Internship"
    if re.search(r"\bpart[- ]time\b", blob):
        return "Part-time"
    if re.search(r"\bcontract(or)?\b|\bfreelance\b", blob):
        return "Contract"
    if re.search(r"\btemporar", blob):
        return "Temporary"
    if re.search(r"\bfull[- ]time\b|\bpermanent\b", blob):
        return "Full-time"
    return ""


def _build_job(
    *,
    company: str,
    position: str,
    location_raw: str,
    address: dict | None,
    apply_candidates: list[str],
    text: str,
    body: str,
    posted_at: str,
    updated_at: str,
    contract: str,
    salary,
    source: str,
    today: date,
    department: str = "",
    deadline: str = "",
) -> Job | None:
    if isinstance(department, dict):
        department = str(department.get("name") or "")
    department = str(department or "")
    apply_url = choose_apply_url(apply_candidates)
    if not apply_url or not is_direct(apply_url) or is_competitor(apply_url):
        return None
    if not company or not position or not posted_at:
        return None
    evidence = classify(text, company=company, known_sponsors=KNOWN_SPONSOR_KEYS)
    if not evidence.publish:
        return None
    posted = _iso_date(posted_at)
    if posted is None:
        return None
    # The ATS list is itself a liveness signal. HTTP checks can still reject it later.
    through = valid_through(posted, today, alive=True)
    if through < today:
        return None
    parsed = parse_location(location_raw, address)
    posting = html_to_text(body)[:12000]
    if salary is None:
        salary = parse_salary(strip_html(text)[:4000])
    summary_bits = [f"{position} at {company}."]
    if parsed.location:
        summary_bits.append(f"Location: {parsed.location}.")
    if evidence.quote:
        summary_bits.append(evidence.quote)
    if evidence.relocation and evidence.relocation_quote:
        summary_bits.append(evidence.relocation_quote)
    if salary:
        summary_bits.append(
            f"Salary: {salary.currency} {salary.min_value}"
            + (f"–{salary.max_value}" if salary.max_value else "")
            + f" per {salary.unit.lower()}."
        )
    return Job(
        company=re.sub(r"\s+", " ", company).strip(),
        position=re.sub(r"\s+", " ", unescape(position)).strip(),
        location=parsed.location or location_raw or "Remote",
        apply_url=canonical_url(apply_url),
        post_date=posted.isoformat(),
        posted_at=posted_at,
        updated_at=updated_at or posted_at,
        valid_through=through.isoformat(),
        sponsorship_evidence=evidence.level,
        sponsorship_quote=evidence.quote,
        visa=visa_label(evidence.level),
        reloc="Relocation assistance" if evidence.relocation else "",
        contract=contract,
        source=source,
        link_status="ats-open",
        summary=" ".join(summary_bits)[:700],
        address=parsed.as_dict(),
        salary=salary.as_dict() if salary else None,
        relocation_quote=evidence.relocation_quote,
        body=posting,
        excerpt=opening_excerpt(posting),
        department=department,
        deadline=deadline[:10] if deadline else "",
        country=parsed.country,
    )


def _greenhouse_location(item: dict) -> str:
    name = (item.get("location") or {}).get("name") or ""
    office = ""
    offices = item.get("offices") or []
    if offices and isinstance(offices[0], dict):
        office = offices[0].get("location") or ""
    if name.strip().lower() == "remote" and office and office.strip().lower() != "remote":
        return f"Remote, {office}"
    # The office string includes the region and country ("San Francisco, California, United States").
    # The location name is often only the city.
    return office or name


def _greenhouse(token: str, fallback_company: str, today: date) -> list[Job]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    payload = fetch_json(url)
    jobs = []
    for item in payload.get("jobs") or []:
        content = item.get("content") or ""
        title = item.get("title") or ""
        meta_bits = []
        contract = ""
        salary = None
        for meta in item.get("metadata") or []:
            name = str(meta.get("name") or "")
            value = meta.get("value")
            if isinstance(value, str):
                rendered = value
            elif isinstance(value, list):
                rendered = " ".join(str(item) for item in value)
            else:
                rendered = "" if value is None else str(value)
            meta_bits.append(f"{name}: {rendered}")
            if re.search(r"time type|employment type|commitment", name, re.I):
                contract = _contract_from_text(rendered)
            if re.search(r"pay|salary|compensation", name, re.I):
                salary = parse_salary(str(rendered))
        text = " ".join([title, content, " ".join(meta_bits)])
        if not contract:
            contract = _contract_from_text(strip_html(content)[:1500], title)
        location = _greenhouse_location(item)
        departments = item.get("departments") or []
        department = ""
        if departments and isinstance(departments[0], dict):
            department = departments[0].get("name") or ""
        posted_at = _iso_stamp(item.get("first_published"))
        updated_at = _iso_stamp(item.get("updated_at")) or posted_at
        job = _build_job(
            company=item.get("company_name") or fallback_company,
            position=title,
            location_raw=location,
            address=None,
            apply_candidates=[item.get("absolute_url") or ""],
            text=text,
            body=content,
            posted_at=posted_at,
            updated_at=updated_at,
            contract=contract,
            salary=salary,
            source=f"greenhouse:{token}",
            today=today,
            department=department,
            deadline=_iso_stamp(item.get("application_deadline")),
        )
        if job:
            jobs.append(job)
    return jobs


def _lever(token: str, fallback_company: str, today: date) -> list[Job]:
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    payload = fetch_json(url)
    jobs = []
    for item in payload if isinstance(payload, list) else []:
        categories = item.get("categories") or {}
        extra = " ".join(
            part.get("text") or ""
            for part in (item.get("lists") or [])
            if isinstance(part, dict)
        )
        text = " ".join(
            [
                item.get("text") or "",
                item.get("descriptionPlain") or "",
                item.get("additionalPlain") or "",
                extra,
                categories.get("commitment") or "",
                categories.get("location") or "",
            ]
        )
        salary_range = item.get("salaryRange") or item.get("salaryRangeDescription")
        salary = None
        if isinstance(salary_range, dict):
            salary = salary_from_numbers(
                salary_range.get("min"),
                salary_range.get("max"),
                salary_range.get("currency") or "",
                salary_range.get("interval"),
            )
        elif isinstance(salary_range, str):
            salary = parse_salary(salary_range)
        country = item.get("country") or ""
        location = categories.get("location") or ""
        if country and country.lower() not in location.lower():
            location = f"{location}, {country}".strip(", ")
        posted_at = _iso_stamp(item.get("createdAt"))
        job = _build_job(
            company=fallback_company,
            position=item.get("text") or "",
            location_raw=location,
            address=None,
            apply_candidates=[item.get("applyUrl") or "", item.get("hostedUrl") or ""],
            text=text,
            body=text,
            posted_at=posted_at,
            updated_at=_iso_stamp(item.get("updatedAt")) or posted_at,
            contract=_contract_from_text(categories.get("commitment") or "", text[:800]),
            salary=salary,
            source=f"lever:{token}",
            today=today,
            department=categories.get("team") or categories.get("department") or "",
        )
        if job:
            jobs.append(job)
    return jobs


def _ashby(token: str, fallback_company: str, today: date) -> list[Job]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{token}"
    payload = fetch_json(url)
    jobs = []
    for item in payload.get("jobs") or []:
        if item.get("isListed") is False:
            continue
        compensation = item.get("compensation") or {}
        salary = None
        summary = ""
        if isinstance(compensation, dict):
            summary = compensation.get("scrapeableCompensationSalarySummary") or compensation.get("compensationTierSummary") or ""
            tiers = compensation.get("compensationTiers") or []
            if tiers and isinstance(tiers, list):
                components = (tiers[0] or {}).get("components") or []
                for component in components:
                    if not isinstance(component, dict):
                        continue
                    salary = salary_from_numbers(
                        component.get("minValue"),
                        component.get("maxValue"),
                        component.get("currencyCode") or "",
                        component.get("interval"),
                    )
                    if salary:
                        break
        if salary is None and summary:
            salary = parse_salary(summary)
        text = " ".join(
            [
                item.get("title") or "",
                item.get("descriptionPlain") or "",
                item.get("descriptionHtml") or "",
                summary,
                item.get("employmentType") or "",
            ]
        )
        posted_at = _iso_stamp(item.get("publishedAt") or item.get("publishedDate"))
        plain = item.get("descriptionPlain") or ""
        job = _build_job(
            company=fallback_company,
            position=item.get("title") or "",
            location_raw=item.get("location") or "",
            address=item.get("address") if isinstance(item.get("address"), dict) else None,
            apply_candidates=[item.get("applyUrl") or "", item.get("jobUrl") or ""],
            text=text,
            body=plain or item.get("descriptionHtml") or "",
            posted_at=posted_at,
            updated_at=_iso_stamp(item.get("updatedAt")) or posted_at,
            contract=_contract_from_text(item.get("employmentType") or ""),
            salary=salary,
            source=f"ashby:{token}",
            today=today,
            department=item.get("department") or item.get("team") or "",
        )
        if job:
            jobs.append(job)
    return jobs


def fetch_board(kind: str, token: str, company: str, today: date) -> list[Job]:
    if kind == "greenhouse":
        return _greenhouse(token, company, today)
    if kind == "lever":
        return _lever(token, company, today)
    if kind == "ashby":
        return _ashby(token, company, today)
    raise ValueError(f"unknown board kind {kind}")


def fetch_all(today: date | None = None, workers: int = 6) -> tuple[list[Job], list[str]]:
    today = today or datetime.now(timezone.utc).date()
    found: list[Job] = []
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(fetch_board, kind, token, company, today): (kind, token)
            for kind, token, company in BOARDS
        }
        for future in as_completed(futures):
            kind, token = futures[future]
            try:
                batch = future.result()
            except Exception as exc:
                errors.append(f"{kind}:{token}: {exc}")
                print(f"  source {kind}:{token} failed: {exc}")
                continue
            print(f"  {kind}:{token} -> {len(batch)} evidenced jobs")
            found.extend(batch)
    return found, errors
