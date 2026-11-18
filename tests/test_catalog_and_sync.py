import unittest
from datetime import date
from pathlib import Path

from scraper.catalog import expire_and_merge, select_board
from scraper.models import Job
from scraper.site_sync import patch_eleventy, patch_tree


def job(**overrides) -> Job:
    data = dict(
        company="Monzo",
        position="Backend Engineer",
        location="London, United Kingdom",
        apply_url="https://job-boards.greenhouse.io/monzo/jobs/1",
        post_date="2026-11-01",
        valid_through="2026-12-16",
        sponsorship_evidence="confirmed",
        sponsorship_quote="We can sponsor visas.",
        visa="Visa sponsorship",
        reloc="Relocation assistance",
        contract="Full-time",
        source="greenhouse:monzo",
        link_status="alive",
        summary="Backend Engineer at Monzo.",
        address={"addressLocality": "London", "addressCountry": "GB"},
    )
    data.update(overrides)
    return Job(**data)


class CatalogTests(unittest.TestCase):
    def test_drops_unevidenced_and_competitor_rows(self):
        existing = [
            {
                "company": "Old",
                "position": "Role",
                "description": "https://www.arbeitnow.com/jobs/companies/old/role",
                "post_date": "2026-08-01",
                "visa": "Visa Sponsorship",
                "reloc": "Relocation Assistance",
                "contract": "Full Time",
            },
            {
                "company": "Stripe",
                "position": "Engineer",
                "description": "https://stripe.com/jobs/search?gh_jid=1",
                "post_date": "2026-08-12",
                "visa": "Visa Sponsorship",
            },
        ]
        fresh = [job()]
        result = expire_and_merge(existing, fresh, date(2026, 11, 18))
        reasons = {row["reason"] for row in result["removed"]}
        self.assertIn("competitor-board", reasons)
        self.assertIn("no-evidence", reasons)
        self.assertEqual(result["jobs"][0]["sponsorship_evidence"], "confirmed")
        self.assertEqual(len(result["added"]), 1)

    def test_expired_evidenced_job_not_in_the_scrape_is_removed(self):
        existing = [job(valid_through="2026-10-01", apply_url="https://jobs.ashbyhq.com/old/1").to_site()]
        result = expire_and_merge(existing, [job()], date(2026, 11, 18))
        self.assertTrue(any(row["reason"] == "expired" for row in result["removed"]))

    def test_jobs_older_than_90_days_are_not_published(self):
        recent = job(posted_at="2026-11-18T16:26:55Z", post_date="2026-11-18")
        stale = job(
            position="Ancient Role",
            apply_url="https://job-boards.greenhouse.io/monzo/jobs/9",
            post_date="2023-04-28",
            posted_at="2023-04-28T08:00:00Z",
        )
        chosen = select_board([recent, stale], today=date(2026, 11, 18))
        self.assertEqual([item.position for item in chosen], ["Backend Engineer"])

    def test_same_url_is_refreshed_not_duplicated(self):
        existing = [job(sponsorship_quote="old").to_site()]
        fresh = job(sponsorship_quote="We can sponsor visas now.")
        result = expire_and_merge(existing, [fresh], date(2026, 11, 18))
        self.assertEqual(len(result["jobs"]), 1)
        self.assertEqual(result["jobs"][0]["sponsorship_quote"], "We can sponsor visas now.")
        self.assertEqual(result["added"], [])


class SiteSyncTests(unittest.TestCase):
    def test_eleventy_stops_using_eu_and_90_days(self):
        sample = '''
      "Europe": "EU", "Canada": "CA", "Qatar": "QA",
    };
    return codes[country] || "EU";
    date.setDate(date.getDate() + 90);
    return new Date(Date.now() + 90 * 86400000).toISOString().split("T")[0];
    eleventyConfig.addFilter("limit", (arr, limit) => {
'''
        patched = patch_eleventy(sample)
        self.assertNotIn('"EU"', patched)
        self.assertIn('return codes[country] || "";', patched)
        self.assertIn("date.getDate() + 45", patched)
        self.assertIn('dateStr + "T12:00:00Z"', patch_eleventy('const normalized = dateStr + "T12:00:00";'))
        self.assertIn("job.country", patch_eleventy("const country = parts[parts.length - 1].trim();"))
        self.assertIn('"United States": "US"', patched)
        self.assertIn('addFilter("employmentType"', patched)
        self.assertEqual(patched.count('addFilter("employmentType"'), 1)
        self.assertEqual(patch_eleventy(patched), patched)

    def test_patch_tree_copies_overlay_and_homepage_claim(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / ".eleventy.js").write_text(
                '"Qatar": "QA",\nreturn codes[country] || "EU";\n'
                'eleventyConfig.addFilter("limit", (arr, limit) => {\n',
                encoding="utf-8",
            )
            home = root / "src" / "index.njk"
            home.write_text(
                '        <div class="text-3xl font-bold text-gray-900 dark:text-white mb-1">100%</div>\n'
                '        <div class="text-gray-600 dark:text-gray-400 text-sm">Visa Sponsored</div>\n'
                '<span class="badge badge-contract">{{ job.contract }}</span>\n',
                encoding="utf-8",
            )
            changed = patch_tree(root)
            text = home.read_text(encoding="utf-8")
            self.assertIn("Sponsorship evidence", text)
            self.assertNotIn(">100%<", text)
            self.assertIn("{% if job.contract %}", text)
            self.assertTrue((root / "src" / "visa-sponsored-jobs" / "job.njk").exists())
            self.assertTrue(any(item.endswith("update-jobs.yml") for item in changed))


if __name__ == "__main__":
    unittest.main()
