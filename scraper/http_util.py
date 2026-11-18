"""Small HTTP helper. Stdlib only, so the GitHub runner needs no extra packages."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

UA = "Mozilla/5.0 (compatible; VisaJobsBot/2.0; +https://visajobs.xyz)"


def fetch(url: str, timeout: float = 30, method: str = "GET", read_limit: int | None = None) -> tuple[int, bytes, str]:
    req = Request(
        url,
        method=method,
        headers={
            "User-Agent": UA,
            "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urlopen(req, timeout=timeout) as response:
            status = getattr(response, "status", 200) or 200
            final = response.geturl()
            body = response.read() if read_limit is None else response.read(read_limit)
            return status, body, final
    except HTTPError as exc:
        body = exc.read(read_limit or 4096) if exc.fp else b""
        return exc.code, body, url
    except URLError:
        return 0, b"", url


def fetch_json(url: str, timeout: float = 40):
    status, body, _final = fetch(url, timeout=timeout)
    if status != 200:
        raise RuntimeError(f"HTTP {status} for {url}")
    return json.loads(body.decode("utf-8", "replace"))
