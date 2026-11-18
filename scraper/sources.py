"""Fetch openings from employer ATS APIs and keep the ones with sponsorship evidence."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from html import unescape

from scraper.boards import BOARDS, KNOWN_SPONSOR_KEYS
from scraper.classify import classify, strip_html
from scraper.http_util import fetch_json
from scraper.locations import parse_location
from scraper.models import Job, valid_through, visa_label
from scraper.salary import parse_salary, salary_from_numbers
from scraper.urls import canonical_url, choose_apply_url, is_competitor, is_direct

def _iso_date(value) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        # Greenhouse and Lever use epoch seconds or milliseconds.
        stamp = float(value)
        if stamp > 10_000_000_000:
            stamp /= 1000
        return datetime.fromtimestamp(stamp, tz=timezone.utc).date()
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
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
    post: date | None,
    contract: str,
    salary,
    source: str,
    today: date,
) -> Job | None:
    apply_url = choose_apply_url(apply_candidates)
    if not apply_url or not is_direct(apply_url) or is_competitor(apply_url):
        return None
    if not company or not position:
        return None
    evidence = classify(text, company=company, known_sponsors=KNOWN_SPONSOR_KEYS)
    if not evidence.publish:
        return None
    posted = post or today
    # The ATS list is itself a liveness signal. HTTP checks can still reject it later.
    through = valid_through(posted, today, alive=True)
    if through < today:
        return None
    parsed = parse_location(location_raw, address)
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
    )


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
        location = (item.get("location") or {}).get("name") or ""
        posted = _iso_date(item.get("first_published") or item.get("updated_at"))
        job = _build_job(
            company=item.get("company_name") or fallback_company,
            position=title,
            location_raw=location,
            address=None,
            apply_candidates=[item.get("absolute_url") or ""],
            text=text,
            post=posted,
            contract=contract,
            salary=salary,
            source=f"greenhouse:{token}",
            today=today,
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
        job = _build_job(
            company=fallback_company,
            position=item.get("text") or "",
            location_raw=location,
            address=None,
            apply_candidates=[item.get("applyUrl") or "", item.get("hostedUrl") or ""],
            text=text,
            post=_iso_date(item.get("createdAt")),
            contract=_contract_from_text(categories.get("commitment") or "", text[:800]),
            salary=salary,
            source=f"lever:{token}",
            today=today,
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
        job = _build_job(
            company=fallback_company,
            position=item.get("title") or "",
            location_raw=item.get("location") or "",
            address=item.get("address") if isinstance(item.get("address"), dict) else None,
            apply_candidates=[item.get("applyUrl") or "", item.get("jobUrl") or ""],
            text=text,
            post=_iso_date(item.get("publishedAt")),
            contract=_contract_from_text(item.get("employmentType") or ""),
            salary=salary,
            source=f"ashby:{token}",
            today=today,
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
