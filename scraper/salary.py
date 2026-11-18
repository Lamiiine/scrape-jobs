"""Pull a yearly (or hourly) salary range out of posting text or ATS fields."""

from __future__ import annotations

import re
from dataclasses import dataclass

CURRENCY = {
    "€": "EUR",
    "£": "GBP",
    "$": "USD",
    "eur": "EUR",
    "gbp": "GBP",
    "usd": "USD",
    "chf": "CHF",
    "cad": "CAD",
    "aud": "AUD",
    "sek": "SEK",
    "nok": "NOK",
    "dkk": "DKK",
    "pln": "PLN",
}

_NUMBER = r"\d{1,3}(?:[.,\s]\d{3})+|\d{2,3}(?=\s*[kK])|\d{4,7}"
RANGE_RE = re.compile(
    r"(?P<cur1>€|£|\$|EUR|USD|GBP|CHF|CAD|AUD)?\s*"
    rf"(?P<min>{_NUMBER})"
    r"\s*(?P<k1>[kK])?"
    r"(?:\s*(?P<cur1b>EUR|USD|GBP|CHF))?"
    r"\s*(?:-|–|—|to)\s*"
    r"(?P<cur2>€|£|\$|EUR|USD|GBP|CHF|CAD|AUD)?\s*"
    rf"(?P<max>{_NUMBER})"
    r"\s*(?P<k2>[kK])?"
    r"(?:\s*(?P<cur2b>EUR|USD|GBP|CHF))?",
    re.I,
)


@dataclass(frozen=True)
class Salary:
    currency: str
    min_value: int
    max_value: int | None
    unit: str

    def as_dict(self) -> dict:
        data = {
            "currency": self.currency,
            "min": self.min_value,
            "unit": self.unit,
        }
        if self.max_value:
            data["max"] = self.max_value
        return data


def _amount(raw: str, kilo: str | None) -> int | None:
    digits = re.sub(r"[^\d]", "", raw or "")
    if not digits:
        return None
    value = int(digits)
    if kilo:
        value *= 1000
    if value < 1000 or value > 2_000_000:
        return None
    return value


def _currency(*tokens: str | None) -> str:
    for token in tokens:
        if not token:
            continue
        key = token.strip().lower()
        if key in CURRENCY:
            return CURRENCY[key]
        if token.strip() in CURRENCY:
            return CURRENCY[token.strip()]
    return "USD"


def parse_salary(text: str) -> Salary | None:
    if not text:
        return None
    match = RANGE_RE.search(text)
    if not match:
        return None
    window = text[max(0, match.start() - 40): match.end() + 40].lower()
    unit = "HOUR" if "hour" in window or "/hr" in window else "YEAR"
    minimum = _amount(match.group("min"), match.group("k1"))
    maximum = _amount(match.group("max"), match.group("k2"))
    if minimum is None:
        return None
    if maximum is not None and maximum < minimum:
        minimum, maximum = maximum, minimum
    currency = _currency(
        match.group("cur1"),
        match.group("cur2"),
        match.group("cur1b"),
        match.group("cur2b"),
    )
    if unit == "YEAR" and minimum < 10000:
        return None
    return Salary(currency, minimum, maximum, unit)


def salary_from_numbers(min_value, max_value, currency: str, interval: str | None = None) -> Salary | None:
    try:
        minimum = int(float(min_value))
    except (TypeError, ValueError):
        return None
    maximum = None
    try:
        if max_value not in (None, ""):
            maximum = int(float(max_value))
    except (TypeError, ValueError):
        maximum = None
    if minimum < 1000:
        return None
    unit = "HOUR" if interval and "hour" in str(interval).lower() else "YEAR"
    code = _currency(currency) if currency else "USD"
    if currency and len(str(currency)) == 3 and str(currency).isalpha():
        code = str(currency).upper()
    return Salary(code, minimum, maximum, unit)
