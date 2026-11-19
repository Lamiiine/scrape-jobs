import unittest
from datetime import date

from scraper.locations import parse_location
from scraper.models import valid_through
from scraper.salary import parse_salary
from scraper.sources import _iso_stamp
from scraper.urls import canonical_url, choose_apply_url, is_competitor, is_direct


class UrlTests(unittest.TestCase):
    def test_competitor_hosts(self):
        for url in (
            "https://www.arbeitnow.com/jobs/companies/acme/role",
            "https://relocate.me/international-jobs/acme",
            "https://visasponsor.jobs/api/jobs/123",
            "https://jaabz.com/job/123",
            "https://europevisajobs.com/jobs/1",
        ):
            self.assertTrue(is_competitor(url), url)
            self.assertFalse(is_direct(url), url)

    def test_prefers_ats_over_competitor(self):
        chosen = choose_apply_url([
            "https://www.arbeitnow.com/jobs/companies/monzo/backend",
            "https://job-boards.greenhouse.io/monzo/jobs/6635595",
        ])
        self.assertIn("greenhouse.io", chosen)

    def test_drops_tracking_params(self):
        url = canonical_url("https://Job-Boards.Greenhouse.io/monzo/jobs/1/?utm_source=x&gh_jid=1")
        self.assertEqual(url, "https://job-boards.greenhouse.io/monzo/jobs/1?gh_jid=1")
        self.assertNotIn("utm_source", url)


class StampTests(unittest.TestCase):
    def test_offset_is_kept_as_utc(self):
        self.assertEqual(_iso_stamp("2026-11-18T11:26:55-05:00"), "2026-11-18T16:26:55Z")

    def test_date_only_is_noon_utc_not_local(self):
        self.assertEqual(_iso_stamp("2026-11-18"), "2026-11-18T12:00:00Z")


class LocationTests(unittest.TestCase):
    def test_california_is_a_region_not_a_country(self):
        parsed = parse_location("San Francisco, California, United States")
        self.assertEqual(parsed.country_code, "US")
        self.assertEqual(parsed.region, "CA")
        self.assertEqual(parsed.locality, "San Francisco")

    def test_berlin_is_germany_not_eu(self):
        parsed = parse_location("Berlin")
        self.assertEqual(parsed.country_code, "DE")
        self.assertNotEqual(parsed.country_code, "EU")
        self.assertIn("Germany", parsed.location)
        self.assertEqual(parsed.region, "")
        self.assertEqual(parsed.as_dict()["addressRegion"], "Berlin")

    def test_named_regions_are_kept(self):
        england = parse_location("London, England, United Kingdom")
        self.assertEqual(england.region, "England")
        self.assertEqual(england.as_dict()["addressRegion"], "England")
        paris = parse_location("Paris, Île-de-France, France")
        self.assertEqual(paris.region, "Île-de-France")
        self.assertEqual(paris.country_code, "FR")
        berlin_state = parse_location("Berlin State, Germany")
        self.assertEqual(berlin_state.region, "Berlin")
        self.assertEqual(berlin_state.as_dict()["addressRegion"], "Berlin")

    def test_remote_keeps_a_region_and_a_country(self):
        parsed = parse_location("Remote, United Kingdom")
        self.assertTrue(parsed.remote)
        self.assertEqual(parsed.country_code, "GB")
        self.assertEqual(parsed.as_dict()["addressRegion"], "Remote")

    def test_us_state(self):
        parsed = parse_location("San Francisco, CA")
        self.assertEqual(parsed.country_code, "US")
        self.assertEqual(parsed.locality, "San Francisco")

    def test_remote_uk(self):
        parsed = parse_location("Remote (UK)")
        self.assertEqual(parsed.country_code, "GB")

    def test_ashby_address(self):
        parsed = parse_location("", {"postalAddress": {
            "addressLocality": "Amsterdam",
            "addressCountry": "Netherlands",
            "postalCode": "1012",
        }})
        self.assertEqual(parsed.country_code, "NL")
        self.assertEqual(parsed.postal_code, "1012")


class SalaryTests(unittest.TestCase):
    def test_euro_range(self):
        salary = parse_salary("The range is €80,000 - €120,000 per year.")
        self.assertIsNotNone(salary)
        self.assertEqual(salary.currency, "EUR")
        self.assertEqual(salary.min_value, 80000)
        self.assertEqual(salary.max_value, 120000)
        self.assertEqual(salary.unit, "YEAR")

    def test_dollar_k(self):
        salary = parse_salary("Compensation $180k–$220k")
        self.assertIsNotNone(salary)
        self.assertEqual(salary.min_value, 180000)
        self.assertEqual(salary.max_value, 220000)
        self.assertEqual(salary.currency, "USD")


class WindowTests(unittest.TestCase):
    def test_window_is_45_days(self):
        posted = date(2026, 11, 1)
        self.assertEqual(valid_through(posted, date(2026, 11, 18), alive=False), date(2026, 12, 16))

    def test_live_job_past_the_window_is_extended(self):
        from datetime import timedelta
        posted = date(2026, 1, 1)
        today = date(2026, 11, 18)
        self.assertEqual(valid_through(posted, today, alive=True), today + timedelta(days=45))
        self.assertEqual(valid_through(posted, today, alive=False), date(2026, 2, 15))


if __name__ == "__main__":
    unittest.main()
