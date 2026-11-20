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

    def test_published_record_always_has_schedule_and_region(self):
        plain = job(contract="").to_site()
        self.assertEqual(plain["employmentType"], "FULL_TIME")
        self.assertEqual(plain["address"]["addressRegion"], "London")
        self.assertNotIn("jobLocationType", plain)
        remote = job(
            contract="Internship",
            location="Remote, United Kingdom",
            country="United Kingdom",
            address={"addressLocality": "Remote", "addressCountry": "GB"},
        ).to_site()
        self.assertEqual(remote["employmentType"], "INTERN")
        self.assertEqual(remote["jobLocationType"], "TELECOMMUTE")
        self.assertEqual(remote["applicantLocationRequirements"], {"@type": "Country", "name": "United Kingdom"})
        self.assertEqual(remote["address"]["addressRegion"], "Remote")
        states = {
            "Part-time": "PART_TIME",
            "Contract": "CONTRACTOR",
            "Temporary": "TEMPORARY",
            "Full-time": "FULL_TIME",
        }
        for contract, expected in states.items():
            self.assertEqual(job(contract=contract).to_site()["employmentType"], expected)

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
        self.assertIn('"United States": "US"', patched)
        self.assertIn('addFilter("employmentType"', patched)
        self.assertEqual(patched.count('addFilter("employmentType"'), 1)
        self.assertIn('return "FULL_TIME"', patched)
        self.assertEqual(patch_eleventy(patched), patched)

    def test_country_code_filter_keeps_reading_the_location_string(self):
        sample = '''
  eleventyConfig.addFilter("countryCode", (location) => {
    const parts = cleaned.split(",");
    const country = parts[parts.length - 1].trim();
    return codes[country] || "";
  });
  eleventyConfig.addFilter("uniqueCountries", (jobs) => {
    jobs.forEach((job) => {
      const parts = cleaned.split(",");
      const country = parts[parts.length - 1].trim();
    });
  });
  eleventyConfig.addFilter("groupByCountry", (jobs) => {
    jobs.forEach((job) => {
      const country = parts[parts.length - 1].trim();
    });
  });
'''
        patched = patch_eleventy(sample)
        country_filter = patched.split('addFilter("uniqueCountries"')[0]
        self.assertIn("const country = parts[parts.length - 1].trim();", country_filter)
        self.assertNotIn("job.country", country_filter)
        self.assertEqual(patched.count("job.country"), 2)
        self.assertEqual(patch_eleventy(patched), patched)

    def test_repairs_country_code_filter_that_reads_job(self):
        broken = '''
  eleventyConfig.addFilter("countryCode", (location) => {
    const parts = cleaned.split(",");
    const country = (job.country || "").trim() || parts[parts.length - 1].trim();
    return codes[country] || "";
  });
  eleventyConfig.addFilter("uniqueCountries", (jobs) => {
    jobs.forEach((job) => {
      const country = (job.country || "").trim() || parts[parts.length - 1].trim();
    });
  });
'''
        patched = patch_eleventy(broken)
        country_filter = patched.split('addFilter("uniqueCountries"')[0]
        self.assertNotIn("job", country_filter)
        self.assertIn("const country = parts[parts.length - 1].trim();", country_filter)
        self.assertIn("job.country", patched.split('addFilter("uniqueCountries"', 1)[1])
        self.assertEqual(patch_eleventy(patched), patched)

    def test_old_employment_filter_defaults_to_full_time(self):
        from scraper.site_sync import EMPLOYMENT_FILTER_OLD
        patched = patch_eleventy(EMPLOYMENT_FILTER_OLD + '\n  eleventyConfig.addFilter("limit", (arr, limit) => {\n')
        self.assertEqual(patched.count('addFilter("employmentType"'), 1)
        self.assertIn('return "FULL_TIME"', patched)
        self.assertNotIn('if (!c) return ""', patched)
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
            job_page = (root / "src" / "visa-sponsored-jobs" / "job.njk").read_text(encoding="utf-8")
            self.assertIn('"employmentType": "{{ emp }}"', job_page)
            self.assertIn('"addressRegion"', job_page)
            self.assertIn('"jobLocationType": "TELECOMMUTE"', job_page)
            self.assertNotIn('{% if emp %}', job_page)

    def test_listing_schema_gains_region_and_always_has_a_schedule(self):
        from scraper.site_sync import EMPLOYMENT_OPTIONAL, INDEX_ADDRESS_OLD, _patch_jobposting
        patched = _patch_jobposting(EMPLOYMENT_OPTIONAL + "\n" + INDEX_ADDRESS_OLD)
        self.assertIn("job.employmentType or (job.contract | employmentType)", patched)
        self.assertNotIn("{% if emp %}", patched)
        self.assertIn('"addressRegion"', patched)


if __name__ == "__main__":
    unittest.main()
