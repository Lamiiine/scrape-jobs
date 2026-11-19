"""Turn free-text locations into a display string and a postal address."""

from __future__ import annotations

import re
from dataclasses import dataclass

COUNTRY_CODES = {
    "germany": "DE",
    "deutschland": "DE",
    "netherlands": "NL",
    "the netherlands": "NL",
    "holland": "NL",
    "united kingdom": "GB",
    "uk": "GB",
    "u.k.": "GB",
    "great britain": "GB",
    "england": "GB",
    "scotland": "GB",
    "wales": "GB",
    "spain": "ES",
    "ireland": "IE",
    "sweden": "SE",
    "switzerland": "CH",
    "portugal": "PT",
    "poland": "PL",
    "denmark": "DK",
    "czech republic": "CZ",
    "czechia": "CZ",
    "france": "FR",
    "austria": "AT",
    "belgium": "BE",
    "finland": "FI",
    "italy": "IT",
    "norway": "NO",
    "bulgaria": "BG",
    "romania": "RO",
    "canada": "CA",
    "australia": "AU",
    "japan": "JP",
    "new zealand": "NZ",
    "united arab emirates": "AE",
    "uae": "AE",
    "singapore": "SG",
    "qatar": "QA",
    "united states": "US",
    "united states of america": "US",
    "usa": "US",
    "us": "US",
    "u.s.": "US",
    "u.s.a.": "US",
    "luxembourg": "LU",
    "estonia": "EE",
    "lithuania": "LT",
    "latvia": "LV",
    "hungary": "HU",
    "croatia": "HR",
    "slovakia": "SK",
    "slovenia": "SI",
    "greece": "GR",
    "malta": "MT",
    "cyprus": "CY",
    "iceland": "IS",
    "india": "IN",
    "brazil": "BR",
    "mexico": "MX",
    "israel": "IL",
    "south korea": "KR",
    "korea": "KR",
    "china": "CN",
    "hong kong": "HK",
    "taiwan": "TW",
    "poland": "PL",
}

US_STATES = {
    "al": "Alabama", "ak": "Alaska", "az": "Arizona", "ar": "Arkansas", "ca": "California",
    "co": "Colorado", "ct": "Connecticut", "dc": "District of Columbia", "de": "Delaware",
    "fl": "Florida", "ga": "Georgia", "hi": "Hawaii", "ia": "Iowa", "id": "Idaho",
    "il": "Illinois", "in": "Indiana", "ks": "Kansas", "ky": "Kentucky", "la": "Louisiana",
    "ma": "Massachusetts", "md": "Maryland", "me": "Maine", "mi": "Michigan", "mn": "Minnesota",
    "mo": "Missouri", "ms": "Mississippi", "mt": "Montana", "nc": "North Carolina",
    "nd": "North Dakota", "ne": "Nebraska", "nh": "New Hampshire", "nj": "New Jersey",
    "nm": "New Mexico", "nv": "Nevada", "ny": "New York", "oh": "Ohio", "ok": "Oklahoma",
    "or": "Oregon", "pa": "Pennsylvania", "ri": "Rhode Island", "sc": "South Carolina",
    "sd": "South Dakota", "tn": "Tennessee", "tx": "Texas", "ut": "Utah", "va": "Virginia",
    "vt": "Vermont", "wa": "Washington", "wi": "Wisconsin", "wv": "West Virginia", "wy": "Wyoming",
}

# Cities that show up without a country on ATS boards.
CITY_COUNTRY = {
    "berlin": ("Berlin", "DE", "Germany"),
    "munich": ("Munich", "DE", "Germany"),
    "münchen": ("Munich", "DE", "Germany"),
    "hamburg": ("Hamburg", "DE", "Germany"),
    "frankfurt": ("Frankfurt", "DE", "Germany"),
    "cologne": ("Cologne", "DE", "Germany"),
    "köln": ("Cologne", "DE", "Germany"),
    "stuttgart": ("Stuttgart", "DE", "Germany"),
    "düsseldorf": ("Düsseldorf", "DE", "Germany"),
    "dusseldorf": ("Düsseldorf", "DE", "Germany"),
    "amsterdam": ("Amsterdam", "NL", "Netherlands"),
    "rotterdam": ("Rotterdam", "NL", "Netherlands"),
    "utrecht": ("Utrecht", "NL", "Netherlands"),
    "eindhoven": ("Eindhoven", "NL", "Netherlands"),
    "london": ("London", "GB", "United Kingdom"),
    "manchester": ("Manchester", "GB", "United Kingdom"),
    "edinburgh": ("Edinburgh", "GB", "United Kingdom"),
    "cambridge": ("Cambridge", "GB", "United Kingdom"),
    "oxford": ("Oxford", "GB", "United Kingdom"),
    "bristol": ("Bristol", "GB", "United Kingdom"),
    "cardiff": ("Cardiff", "GB", "United Kingdom"),
    "dublin": ("Dublin", "IE", "Ireland"),
    "cork": ("Cork", "IE", "Ireland"),
    "paris": ("Paris", "FR", "France"),
    "lyon": ("Lyon", "FR", "France"),
    "madrid": ("Madrid", "ES", "Spain"),
    "barcelona": ("Barcelona", "ES", "Spain"),
    "lisbon": ("Lisbon", "PT", "Portugal"),
    "lisboa": ("Lisbon", "PT", "Portugal"),
    "porto": ("Porto", "PT", "Portugal"),
    "stockholm": ("Stockholm", "SE", "Sweden"),
    "gothenburg": ("Gothenburg", "SE", "Sweden"),
    "copenhagen": ("Copenhagen", "DK", "Denmark"),
    "oslo": ("Oslo", "NO", "Norway"),
    "helsinki": ("Helsinki", "FI", "Finland"),
    "zurich": ("Zurich", "CH", "Switzerland"),
    "zürich": ("Zurich", "CH", "Switzerland"),
    "geneva": ("Geneva", "CH", "Switzerland"),
    "vienna": ("Vienna", "AT", "Austria"),
    "wien": ("Vienna", "AT", "Austria"),
    "brussels": ("Brussels", "BE", "Belgium"),
    "prague": ("Prague", "CZ", "Czech Republic"),
    "warsaw": ("Warsaw", "PL", "Poland"),
    "warszawa": ("Warsaw", "PL", "Poland"),
    "milan": ("Milan", "IT", "Italy"),
    "rome": ("Rome", "IT", "Italy"),
    "toronto": ("Toronto", "CA", "Canada"),
    "vancouver": ("Vancouver", "CA", "Canada"),
    "montreal": ("Montreal", "CA", "Canada"),
    "sydney": ("Sydney", "AU", "Australia"),
    "melbourne": ("Melbourne", "AU", "Australia"),
    "singapore": ("Singapore", "SG", "Singapore"),
    "tokyo": ("Tokyo", "JP", "Japan"),
    "remote": ("Remote", "", ""),
}

# Regions that are not US states. The value is what Google should see in addressRegion.
REGION_NAMES = {
    "england": "England",
    "scotland": "Scotland",
    "wales": "Wales",
    "northern ireland": "Northern Ireland",
    "ile-de-france": "Île-de-France",
    "ile de france": "Île-de-France",
    "berlin state": "Berlin",
    "state of berlin": "Berlin",
    "land berlin": "Berlin",
    "bavaria": "Bavaria",
    "bayern": "Bavaria",
    "baden-wurttemberg": "Baden-Württemberg",
    "north rhine-westphalia": "North Rhine-Westphalia",
    "nordrhein-westfalen": "North Rhine-Westphalia",
    "hesse": "Hesse",
    "hessen": "Hesse",
    "ontario": "Ontario",
    "british columbia": "British Columbia",
    "quebec": "Quebec",
    "new south wales": "New South Wales",
    "victoria": "Victoria",
}

_STATE_BY_NAME = {name.lower(): abbr.upper() for abbr, name in US_STATES.items()}

CODE_TO_NAME = {}
for _name, _code in COUNTRY_CODES.items():
    CODE_TO_NAME.setdefault(_code, _name.title() if len(_name) > 3 else _name.upper())
CODE_TO_NAME.update({
    "GB": "United Kingdom",
    "US": "United States",
    "DE": "Germany",
    "NL": "Netherlands",
    "AE": "United Arab Emirates",
    "CZ": "Czech Republic",
    "KR": "South Korea",
})


@dataclass(frozen=True)
class Address:
    location: str
    locality: str
    region: str
    country: str
    country_code: str
    postal_code: str = ""
    remote: bool = False

    def as_dict(self) -> dict:
        locality = self.locality or ("Remote" if self.remote else "")
        # Google requires addressRegion. A known state wins; otherwise repeat the city.
        region = self.region or locality or "Remote"
        data = {
            "addressLocality": locality or region,
            "addressRegion": region,
            "addressCountry": self.country_code,
        }
        if self.postal_code:
            data["postalCode"] = self.postal_code
        return data


def _clean(value: str) -> str:
    value = re.sub(r"[\U0001F1E0-\U0001FAFF]", "", value or "")
    value = value.replace("\xa0", " ")
    return re.sub(r"\s+", " ", value).strip(" ,;/")


def _country_from_token(token: str) -> tuple[str, str]:
    key = token.strip().lower().rstrip(".")
    code = COUNTRY_CODES.get(key)
    if not code:
        return "", ""
    return code, CODE_TO_NAME.get(code, token.strip())


def _fold(value: str) -> str:
    value = (value or "").lower().strip()
    return (
        value.replace("î", "i")
        .replace("ï", "i")
        .replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
        .replace("ü", "u")
        .replace("ö", "o")
        .replace("ä", "a")
    )


def _region_in_parts(parts: list[str], locality: str) -> str:
    city = _fold(locality)
    for part in parts:
        key = _fold(part)
        label = REGION_NAMES.get(key)
        if not label:
            continue
        # "Berlin" the city is not a region. "Berlin State" is.
        if key == city and key == _fold(label):
            continue
        return label
    return ""


def parse_location(raw: str, address: dict | None = None) -> Address:
    """Build a display location and ISO country. Never emits country code EU."""
    remote = bool(re.search(r"\bremote\b|\btelecommut", (raw or "").lower()))
    if isinstance(address, dict):
        postal = address.get("postalAddress") if isinstance(address.get("postalAddress"), dict) else address
        locality = _clean(str(postal.get("addressLocality") or postal.get("city") or ""))
        region = _clean(str(postal.get("addressRegion") or postal.get("region") or ""))
        country_raw = _clean(str(postal.get("addressCountry") or postal.get("country") or ""))
        postal_code = _clean(str(postal.get("postalCode") or ""))
        code, country_name = _country_from_token(country_raw)
        if not code and len(country_raw) == 2:
            code, country_name = _country_from_token(country_raw)
        if locality or code:
            parts = [p for p in (locality, region, country_name) if p]
            display = ", ".join(parts) if parts else _clean(raw) or "Remote"
            if remote and not display.lower().startswith("remote"):
                display = f"Remote, {display}"
            return Address(display, locality, region, country_name, code, postal_code, remote)

    text = _clean(raw)
    if not text or text.lower() in {"hybrid", "on-site", "onsite", "n/a", "various"}:
        return Address("Remote" if not text else text, "", "", "", "", remote=remote or not text)

    lowered = text.lower()
    named_city = None
    for token, info in CITY_COUNTRY.items():
        if token == "remote":
            continue
        if re.search(rf"\b{re.escape(token)}\b", lowered):
            named_city = info
            break
    if "remote" in lowered and named_city is None:
        code, country_name = "", ""
        for token in ("united kingdom", "uk", "germany", "netherlands", "united states", "usa", "ireland", "france", "spain"):
            if re.search(rf"\b{re.escape(token)}\b", lowered):
                code, country_name = _country_from_token(token)
                break
        label = "Remote" + (f", {country_name}" if country_name else "")
        return Address(label, "Remote", "", country_name, code, remote=True)

    parts = [p.strip() for p in re.split(r"[,;/|]", text) if p.strip()]
    code, country_name = "", ""
    region = ""
    locality = parts[0] if parts else text
    for part in parts:
        key = part.lower()
        if key in CITY_COUNTRY and key != "remote":
            city, code, country_name = CITY_COUNTRY[key]
            locality = city
            break
    if not code:
        for part in parts:
            if len(part) == 2 and part.lower() in US_STATES:
                region = part.upper()
                code, country_name = "US", "United States"
                break
    if not region:
        for part in parts:
            abbr = _STATE_BY_NAME.get(part.lower())
            if abbr:
                region = abbr
                if not code:
                    code, country_name = "US", "United States"
                break
    if not code:
        for part in reversed(parts):
            code, country_name = _country_from_token(part)
            if code:
                break
    if not region:
        region = _region_in_parts(parts, locality)
        if region and _fold(locality).startswith(_fold(region)):
            locality = region

    if country_name and country_name.lower() not in locality.lower():
        display_parts = [locality]
        if region and region.lower() not in locality.lower():
            display_parts.append(region)
        display_parts.append(country_name)
        display = ", ".join(display_parts)
    else:
        display = text
    if remote and display and not display.lower().startswith("remote"):
        display = f"Remote, {display}"
    return Address(display, locality, region, country_name, code, remote=remote)
