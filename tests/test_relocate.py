import unittest
from datetime import date

from scraper.relocate import job_from_page, parse_sitemap


PAGE = """
<script type="application/ld+json">{"@type":"JobPosting","title":"Staff AI Engineer","datePosted":"2026-11-01","employmentType":"FULL_TIME","hiringOrganization":{"name":"Picnic"},"description":"<p>Build shopping agents.</p>","jobLocation":{"address":{"addressLocality":"Amsterdam","addressCountry":"Netherlands"}}}</script>
<a href="https://jobs.picnic.app/nl/vacancies?gh_jid=8179444&amp;gh_src=abc" class="job-apply__button">Apply</a>
<section class="job-package"><h2>Advanced relocation package</h2><ul>
<li><span>Visa services</span></li><li><span>Flight ticket</span></li>
</ul></section>
"""

SITEMAP = """
<urlset>
  <url><loc>https://relocate.me/netherlands/amsterdam/picnic/staff-ai-engineer-10305</loc><lastmod>2026-11-19</lastmod></url>
  <url><loc>https://relocate.me/remote/remote/the-global-move/archive</loc><lastmod>2026-11-19</lastmod></url>
</urlset>
"""


class RelocateTests(unittest.TestCase):
    def test_sitemap_pairs_each_job_with_its_date(self):
        pages = parse_sitemap(SITEMAP)
        self.assertEqual(pages[0][1], "2026-11-19")
        self.assertEqual(len(pages), 2)

    def test_page_keeps_the_employer_link_and_visa_line(self):
        job = job_from_page(PAGE, date(2026, 11, 23))
        self.assertIsNotNone(job)
        self.assertEqual(job.company, "Picnic")
        self.assertEqual(job.location, "Amsterdam, Netherlands")
        self.assertEqual(job.contract, "Full-time")
        self.assertEqual(job.sponsorship_evidence, "confirmed")
        self.assertIn("Visa services", job.sponsorship_quote)
        self.assertTrue(job.apply_url.startswith("https://jobs.picnic.app/"))
        self.assertNotIn("gh_src", job.apply_url)
        self.assertEqual(job.source, "relocate.me")

    def test_competitor_apply_link_is_dropped(self):
        html = PAGE.replace("https://jobs.picnic.app/nl/vacancies?gh_jid=8179444&amp;gh_src=abc", "https://jaabz.com/jobs/1")
        self.assertIsNone(job_from_page(html, date(2026, 11, 23)))
