"""Decide whether a posting actually offers visa sponsorship.

Evidence levels written onto each job:

- confirmed: the title or description says so, and that sentence is not a refusal
- likely: the employer is on the known-sponsor list and the posting does not refuse sponsorship
- unverified: nothing supports a sponsorship claim (these jobs are not published)
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from html import unescape

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")

# Sentences that mention visas/sponsorship but are not an offer.
DENIAL_RE = re.compile(
    r"("
    r"not\s+provided|not\s+available|not\s+offered|not\s+eligible|"
    r"unable\s+to|not\s+able\s+to|"
    r"cannot|can\s*not|can't|"
    r"will\s+not|won't|"
    r"do(?:es)?\s+not|don't|doesn't|"
    r"no\s+visa|no\s+sponsorship|"
    r"without\s+(?:the\s+need\s+for\s+)?(?:new\s+)?(?:visa\s+)?sponsorship|"
    r"without\s+company\s+sponsorship|"
    r"must\s+(?:already\s+)?(?:be\s+)?(?:currently\s+)?(?:authorized|authorised|eligible)|"
    r"must\s+have\s+(?:the\s+)?(?:unrestricted\s+)?right\s+to\s+work|"
    r"already\s+(?:have|possess|hold)\s+(?:the\s+)?(?:full\s+)?(?:right|authori[sz]ation)|"
    r"sponsorship\s+is\s+not|"
    r"we\s+(?:are|are\s+not|aren't)\s+(?:unable|not)\s+able|"
    r"will\s+not\s+sponsor|does\s+not\s+sponsor|do\s+not\s+sponsor|"
    r"unable\s+to\s+sponsor|cannot\s+sponsor"
    r")",
    re.I,
)

# "sponsorship" / "sponsor" used for something other than a work visa.
FALSE_FRIEND_RE = re.compile(
    r"("
    r"executive\s+sponsor|c-?\s*suite\s+sponsorship|project\s+sponsor|"
    r"named\s+sponsor|internal\s+sponsor|"
    r"sponsored\s+(?:media|content|post|article|campaign)|"
    r"export\s+licen[cs]e|"
    r"sponsor(?:ed|ing)?\s+(?:a\s+)?(?:project|team|initiative|event)"
    r")",
    re.I,
)

CONFIRMED_RE = re.compile(
    r"("
    r"we\s+can\s+sponsor\s+(?:your\s+|a\s+)?visas?|"
    r"we\s+(?:do|will)\s+sponsor\s+(?:your\s+|a\s+)?visas?|"
    r"we(?:'ll|\s+will)\s+sponsor\s+(?:your\s+)?(?:work\s+)?visas?|"
    r"visa\s+sponsorship(?:\s+is|\s+&|\s+and)?\s*(?:available|provided|offered|included)|"
    r"(?:provide|provides|providing|offer|offers|offering)\s+visa\s+sponsorship|"
    r"visa\s+sponsorship\s+(?:and|&)\s+relocation|"
    r"sponsorship\s+(?:is\s+)?available|"
    r"visa\s+support|"
    r"relocation\s+package\s+with\s+visa|"
    r"sponsor(?:ing)?\s+(?:a\s+|your\s+|the\s+)?work\s+(?:visa|permit)|"
    r"work\s+permit\s+sponsorship|"
    r"(?:eu\s+)?blue\s+card|"
    r"skilled\s+worker\s+visa|"
    r"h-?1b\s+(?:visa\s+)?sponsorship|"
    r"visa[-\s]?unterst[uü]tzung|"
    r"visumsponsoring|"
    r"sponsorship\s+for\s+(?:a\s+)?(?:work\s+)?visa"
    r")",
    re.I,
)

RELOC_POS_RE = re.compile(
    r"("
    r"relocation\s+(?:assistance|support|package|allowance|benefit|budget|bonus|stipend)|"
    r"moving\s+(?:allowance|expenses|stipend|bonus)|"
    r"(?:we(?:'ll|\s+will|\s+can)|(?:i'll))?\s*help\s+you\s+relocate|"
    r"we(?:'ll|\s+will)\s+help\s+you\s+relocate|"
    r"relocation\s+provided|"
    r"umzugspaket|"
    r"relocation\s+package\s+with\s+visa"
    r")",
    re.I,
)

# "willing to relocate" and "relocation is required" are not an employer package.
RELOC_NEG_RE = re.compile(
    r"("
    r"willing\s+to\s+relocate|"
    r"must\s+relocate|"
    r"relocation\s+(?:is\s+)?required|"
    r"relocation\s+will\s+be\s+required|"
    r"required\s+to\s+relocate|"
    r"it\s+will\s+require\s+a\s+relocation"
    r")",
    re.I,
)

VISA_WORD_RE = re.compile(r"\b(visa|visum|sponsorship|sponsor|blue\s+card|work\s+permit)\b", re.I)


@dataclass(frozen=True)
class Evidence:
    level: str
    quote: str
    relocation: bool
    relocation_quote: str

    @property
    def publish(self) -> bool:
        return self.level in ("confirmed", "likely")


def strip_html(value: str) -> str:
    text = value or ""
    text = text.replace("\xa0", " ").replace("&nbsp;", " ").replace("&#39;", "'")
    text = unescape(unescape(text))
    text = text.replace("\xa0", " ")
    text = TAG_RE.sub(" ", text)
    text = WS_RE.sub(" ", text)
    return text.strip()


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\s*[|•●]\s+|\n+", text)
    return [p.strip() for p in parts if p and p.strip()]


def _around(sentence: str, match: re.Match) -> str:
    start = max(0, match.start() - 70)
    end = min(len(sentence), match.end() + 90)
    return _clip(sentence[start:end].strip(" -;,."))


def _clip(sentence: str, limit: int = 240) -> str:
    sentence = WS_RE.sub(" ", sentence).strip()
    if len(sentence) <= limit:
        return sentence
    return sentence[: limit - 1].rstrip() + "…"


def company_key(name: str) -> str:
    folded = unicodedata.normalize("NFKD", name or "")
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", folded.lower())


def classify(text: str, company: str = "", known_sponsors: set[str] | None = None) -> Evidence:
    """Classify sponsorship evidence in posting text.

    ``known_sponsors`` holds ``company_key`` values. A match without an explicit
    refusal is ``likely``. An explicit refusal blocks ``likely``.
    """
    plain = strip_html(text)
    sentences = _sentences(plain) or [plain]
    confirmed_quote = ""
    denial = False
    reloc_quote = ""

    for sentence in sentences:
        if not sentence:
            continue
        reloc_match = RELOC_POS_RE.search(sentence)
        if reloc_match and not RELOC_NEG_RE.search(sentence):
            if not reloc_quote:
                reloc_quote = _around(sentence, reloc_match)
        if not VISA_WORD_RE.search(sentence):
            continue
        if DENIAL_RE.search(sentence):
            denial = True
            continue
        if FALSE_FRIEND_RE.search(sentence) and not CONFIRMED_RE.search(sentence):
            continue
        match = CONFIRMED_RE.search(sentence)
        if match and not confirmed_quote:
            confirmed_quote = _around(sentence, match)

    relocation = bool(reloc_quote)
    if confirmed_quote:
        return Evidence("confirmed", confirmed_quote, relocation, reloc_quote)

    sponsors = known_sponsors or set()
    if company_key(company) in sponsors and not denial:
        quote = (
            f"{company} is on the VisaJobs known-sponsor list. "
            "This posting does not itself state visa sponsorship."
        )
        return Evidence("likely", quote, relocation, reloc_quote)

    return Evidence("unverified", "", relocation, reloc_quote)
