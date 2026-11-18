"""Apply-link hygiene: direct employer/ATS URLs, competitor boards, dedupe keys."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

# Boards that compete with visajobs.xyz. Never preferred as the apply link.
COMPETITOR_HOSTS = {
    "arbeitnow.com",
    "arbeitnow.co.uk",
    "relocate.me",
    "visasponsor.jobs",
    "jaabz.com",
    "europevisajobs.com",
    "landing.jobs",
    "relomote.com",
    "visa-sponsored.com",
    "sponsorshipjobs.com",
    "usponsorme.com",
    "honeypot.io",
    "h1bgrader.com",
}

# Not competitor boards, but also not the employer's own application.
AGGREGATOR_HOSTS = {
    "linkedin.com",
    "indeed.com",
    "glassdoor.com",
    "glassdoor.co.uk",
    "simplyhired.com",
    "monster.com",
    "stepstone.de",
    "stepstone.com",
    "totaljobs.com",
    "reed.co.uk",
    "jobleads.com",
}

DIRECT_HOST_MARKERS = (
    "greenhouse.io",
    "lever.co",
    "ashbyhq.com",
    "workable.com",
    "personio.de",
    "personio.com",
    "smartrecruiters.com",
    "myworkdayjobs.com",
    "teamtailor.com",
    "recruitee.com",
    "bamboohr.com",
    "jobvite.com",
    "icims.com",
    "taleo.net",
    "successfactors.com",
    "successfactors.eu",
    "oraclecloud.com",
    "comeet.com",
    "breezy.hr",
    "join.com",
    "ashbyhq.com",
)

DROP_QUERY = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "utm_term",
    "utm_id",
    "gh_src",
    "lever-source",
    "lever-origin",
    "source",
}


def host_of(url: str) -> str:
    try:
        host = urlparse(url).hostname or ""
    except ValueError:
        return ""
    host = host.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def _matches(host: str, names: set[str]) -> bool:
    return any(host == name or host.endswith("." + name) for name in names)


def is_competitor(url: str) -> bool:
    return _matches(host_of(url), COMPETITOR_HOSTS)


def is_aggregator(url: str) -> bool:
    return _matches(host_of(url), AGGREGATOR_HOSTS)


def is_direct(url: str) -> bool:
    if not url or not url.startswith("http"):
        return False
    if is_competitor(url) or is_aggregator(url):
        return False
    return True


def canonical_url(url: str) -> str:
    raw = (url or "").strip().replace("&amp;", "&")
    if not raw:
        return ""
    parts = urlparse(raw)
    if not parts.scheme or not parts.netloc:
        return raw
    query = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k.lower() not in DROP_QUERY
    ]
    path = parts.path.rstrip("/") or "/"
    return urlunparse(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            path,
            "",
            urlencode(query),
            "",
        )
    )


def choose_apply_url(candidates: list[str]) -> str:
    """Prefer a direct employer/ATS URL. Competitor boards are a last resort."""
    cleaned = []
    for url in candidates:
        url = (url or "").strip().replace("&amp;", "&")
        if url.startswith("http"):
            cleaned.append(url)
    direct = [url for url in cleaned if is_direct(url)]
    if direct:
        return direct[0]
    non_competitor = [url for url in cleaned if not is_competitor(url)]
    if non_competitor:
        return non_competitor[0]
    return cleaned[0] if cleaned else ""
