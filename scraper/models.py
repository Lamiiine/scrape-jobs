"""Job records stored in this repo and published to the site."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta


WINDOW_DAYS = 45


@dataclass
class Job:
    company: str
    position: str
    location: str
    apply_url: str
    post_date: str
    valid_through: str
    sponsorship_evidence: str
    sponsorship_quote: str
    visa: str
    reloc: str
    contract: str
    source: str
    link_status: str
    summary: str
    address: dict = field(default_factory=dict)
    salary: dict | None = None
    relocation_quote: str = ""
    posted_at: str = ""
    updated_at: str = ""
    body: str = ""
    excerpt: str = ""
    department: str = ""
    deadline: str = ""
    country: str = ""

    def to_site(self) -> dict:
        """Shape expected by the Eleventy site.

        ``description`` stays the apply URL because existing templates use it
        as the link. The posting text lives in ``body``. ``posted_at`` is the
        employer timestamp; ``post_date`` is that same instant's calendar day.
        """
        record = {
            "company": _plain(self.company),
            "position": _plain(self.position),
            "location": _plain(self.location),
            "country": _plain(self.country),
            "contract": _plain(self.contract),
            "reloc": _plain(self.reloc),
            "visa": _plain(self.visa),
            "post_date": self.post_date,
            "posted_at": self.posted_at or (f"{self.post_date}T12:00:00Z" if self.post_date else ""),
            "updated_at": self.updated_at,
            "valid_through": self.valid_through,
            "logo": "",
            "description": self.apply_url,
            "apply_url": self.apply_url,
            "sponsorship_evidence": self.sponsorship_evidence,
            "sponsorship_quote": _plain(self.sponsorship_quote),
            "summary": _plain(self.summary),
            "body": _body(self.body),
            "excerpt": _plain(self.excerpt),
            "address": _address_for_site(self.address, self.location),
            "employmentType": employment_type(self.contract),
            "source": self.source,
            "link_status": self.link_status,
        }
        if _is_remote(self.location, record["address"]):
            record["jobLocationType"] = "TELECOMMUTE"
            record["applicantLocationRequirements"] = {
                "@type": "Country",
                "name": _plain(self.country) or record["address"].get("addressCountry") or "Remote",
            }
        if self.department:
            record["department"] = _plain(self.department)
        if self.deadline:
            record["deadline"] = self.deadline
        if self.relocation_quote:
            record["relocation_quote"] = _plain(self.relocation_quote)
        if self.salary:
            record["salary"] = self.salary
        return record

    def to_local(self) -> dict:
        return self.to_site()


def _address_for_site(address: dict | None, location: str) -> dict:
    data = {
        key: _plain(value) if isinstance(value, str) else value
        for key, value in (address or {}).items()
    }
    city = data.get("addressLocality") or _city(location)
    region = data.get("addressRegion") or city or "Remote"
    data["addressLocality"] = city or region
    data["addressRegion"] = region
    data.setdefault("addressCountry", "")
    return data


def _city(location: str) -> str:
    part = (location or "").split(",")[0].strip()
    if part.lower().startswith("remote"):
        rest = (location or "").split(",")[1:]
        if rest and rest[0].strip() and rest[0].strip().lower() not in {"united kingdom", "uk", "germany", "united states"}:
            return rest[0].strip()
        return "Remote"
    return part


def _is_remote(location: str, address: dict) -> bool:
    if "remote" in (location or "").lower():
        return True
    return str(address.get("addressLocality") or "").lower() == "remote"


def _plain(value: str) -> str:
    return (value or "").replace("<", "").replace(">", "").replace("\r", " ").replace("\n", " ").strip()


def _body(value: str) -> str:
    text = (value or "").replace("\r\n", "\n").replace("\r", "\n").replace("<", "").replace(">", "")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    # Re-import locally to avoid a cycle; models stays free of the classifier.
    cleaned = "\n".join(lines)
    while "\n\n\n" in cleaned:
        cleaned = cleaned.replace("\n\n\n", "\n\n")
    return cleaned.strip()


def visa_label(level: str) -> str:
    if level == "confirmed":
        return "Visa sponsorship"
    if level == "likely":
        return "Visa sponsorship (likely)"
    return ""


def employment_type(contract: str) -> str:
    """Schema.org employmentType. Unknown schedules are full-time."""
    text = (contract or "").lower()
    if re.search(r"intern", text):
        return "INTERN"
    if re.search(r"part[-_ ]?time", text):
        return "PART_TIME"
    if re.search(r"contract|freelance", text):
        return "CONTRACTOR"
    if re.search(r"\btemp", text):
        return "TEMPORARY"
    return "FULL_TIME"


def valid_through(post_date: date, today: date, alive: bool) -> date:
    """Posting date plus 45 days. Live ATS jobs past that window are extended."""
    window = post_date + timedelta(days=WINDOW_DAYS)
    if alive and window < today:
        return today + timedelta(days=WINDOW_DAYS)
    return window


def parse_iso(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None
