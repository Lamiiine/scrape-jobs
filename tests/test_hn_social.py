import unittest

from scraper.hn import parse_comment
from scraper.models import Job
from scraper.slug import job_slug
from scraper.social import linkedin_text, telegram_text


THUNDER = (
    '<p>Thunder Compute (YC S24) | C++ Systems Engineer | San Francisco (Onsite) | '
    'Full-time | Visa sponsorship | '
    '<a href="https:&#x2F;&#x2F;www.thundercompute.com">site</a></p>'
    '<p>We run a GPU cloud.</p>'
)


class HnParseTests(unittest.TestCase):
    def test_comment_keeps_the_company_site(self):
        parsed = parse_comment(THUNDER, "2026-11-02T16:00:00Z")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["company"], "Thunder Compute")
        messy = parse_comment(
            "<p>Curiosity ( https://curiosity.ai/ ) | Engineer | Toulouse | Visa sponsorship | "
            '<a href="https://curiosity.ai/">site</a></p>',
            "2026-11-02T16:00:00Z",
        )
        self.assertEqual(messy["company"], "Curiosity")
        hidden = parse_comment(
            "<p>Confidential (established group) | Engineer | Khobar | Relocation + visa provided | "
            '<a href="https://example.com/jobs">jobs</a></p>',
            "2026-11-02T16:00:00Z",
        )
        self.assertIsNone(hidden)
        self.assertEqual(parsed["position"], "C++ Systems Engineer")
        self.assertIn("San Francisco", parsed["location"])
        self.assertEqual(parsed["links"], ["https://www.thundercompute.com"])
        self.assertIn("Visa sponsorship", parsed["text"])

    def test_linkedin_and_hn_links_are_not_applications(self):
        html = (
            "<p>Acme | Engineer | Berlin | Visa sponsorship | "
            '<a href="https://news.ycombinator.com/item?id=1">thread</a> '
            '<a href="https://www.linkedin.com/jobs/view/1">linkedin</a></p>'
        )
        self.assertIsNone(parse_comment(html, "2026-11-02T16:00:00Z"))

    def test_missing_link_is_skipped(self):
        html = "<p>Flow Traders | Research Engineer | Hong Kong | Visa | Relocation</p>"
        self.assertIsNone(parse_comment(html, "2026-11-02T16:00:00Z"))


class SlugTests(unittest.TestCase):
    def test_matches_the_live_anthropic_page(self):
        job = Job(
            company="Anthropic",
            position="Applied AI Engineer, Commercial",
            location="San Francisco, CA, United States",
            apply_url="https://job-boards.greenhouse.io/anthropic/jobs/5483945008",
            post_date="2026-11-18",
            valid_through="2027-01-02",
            sponsorship_evidence="confirmed",
            sponsorship_quote="",
            visa="Visa sponsorship",
            reloc="",
            contract="",
            source="greenhouse:anthropic",
            link_status="alive",
            summary="",
        )
        self.assertEqual(
            job_slug(job),
            "anthropic-applied-ai-engineer-commercial-san-francisco-ca-united-states-1e1w",
        )


class SocialTests(unittest.TestCase):
    def test_digest_escapes_html_and_names_the_page(self):
        job = Job(
            company="A&B",
            position="Role <lead>",
            location="Berlin",
            apply_url="https://job-boards.greenhouse.io/anthropic/jobs/5483945008",
            post_date="2026-11-18",
            valid_through="2027-01-02",
            sponsorship_evidence="confirmed",
            sponsorship_quote="",
            visa="Visa sponsorship",
            reloc="Relocation assistance",
            contract="",
            source="hn:1",
            link_status="alive",
            summary="",
        )
        text = telegram_text([job], extra=3)
        self.assertIn("A&amp;B", text)
        self.assertIn("Role &lt;lead&gt;", text)
        self.assertIn("https://visajobs.xyz/visa-sponsored-jobs/", text)
        self.assertIn("And 3 more", text)
        self.assertNotIn("<lead>", text)
        plain = linkedin_text([job], extra=0)
        self.assertIn("A&B", plain)
        self.assertIn("relocation", plain)


if __name__ == "__main__":
    unittest.main()
