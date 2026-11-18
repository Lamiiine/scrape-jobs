"""Employer ATS boards fetched directly. Tokens are public job-board slugs."""

from __future__ import annotations

# company_key() values. Used only when a posting does not itself state sponsorship
# and does not refuse it. Kept short on purpose: a long list would mark every
# opening at a big employer as "likely".
KNOWN_SPONSOR_KEYS = {
    "monzo",
    "n26",
    "anthropic",
}

# (kind, token, display name). Display name is a fallback when the API omits one.
BOARDS: list[tuple[str, str, str]] = [
    ("greenhouse", "monzo", "Monzo"),
    ("greenhouse", "stripe", "Stripe"),
    ("greenhouse", "cloudflare", "Cloudflare"),
    ("greenhouse", "databricks", "Databricks"),
    ("greenhouse", "gitlab", "GitLab"),
    ("greenhouse", "elastic", "Elastic"),
    ("greenhouse", "mongodb", "MongoDB"),
    ("greenhouse", "contentful", "Contentful"),
    ("greenhouse", "datadog", "Datadog"),
    ("greenhouse", "discord", "Discord"),
    ("greenhouse", "coinbase", "Coinbase"),
    ("greenhouse", "airbnb", "Airbnb"),
    ("greenhouse", "figma", "Figma"),
    ("greenhouse", "reddit", "Reddit"),
    ("greenhouse", "pinterest", "Pinterest"),
    ("greenhouse", "robinhood", "Robinhood"),
    ("greenhouse", "block", "Block"),
    ("greenhouse", "twilio", "Twilio"),
    ("greenhouse", "okta", "Okta"),
    ("greenhouse", "anthropic", "Anthropic"),
    ("greenhouse", "scaleai", "Scale AI"),
    ("greenhouse", "brex", "Brex"),
    ("greenhouse", "chime", "Chime"),
    ("greenhouse", "nubank", "Nubank"),
    ("greenhouse", "wise", "Wise"),
    ("greenhouse", "n26", "N26"),
    ("greenhouse", "adyen", "Adyen"),
    ("greenhouse", "hellofresh", "HelloFresh"),
    ("greenhouse", "sumup", "SumUp"),
    ("greenhouse", "celonis", "Celonis"),
    ("greenhouse", "wolt", "Wolt"),
    ("greenhouse", "canonical", "Canonical"),
    ("greenhouse", "trustpilot", "Trustpilot"),
    ("greenhouse", "getyourguide", "GetYourGuide"),
    ("lever", "spotify", "Spotify"),
    ("lever", "palantir", "Palantir"),
    ("ashby", "notion", "Notion"),
    ("ashby", "linear", "Linear"),
    ("ashby", "openai", "OpenAI"),
    ("ashby", "ramp", "Ramp"),
    ("ashby", "vercel", "Vercel"),
]
