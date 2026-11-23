import unittest
from datetime import date
from pathlib import Path

from scraper.models import Job
from scraper.post_template import render_linkedin, render_telegram, render_telegram_preview
from scraper.social import (
    announce,
    job_id,
    linkedin_commentary,
    organization_id,
    select_roles,
    telegram_fields,
)
from scraper.urls import canonical_url


THURSDAY = date(2026, 11, 19)
SATURDAY = date(2026, 11, 21)


def job(
    position,
    company="Anthropic",
    location="Berlin, Germany",
    evidence="confirmed",
    salary=None,
    reloc="",
    url="https://jobs.example.com/1",
    posted="2026-11-19T09:00:00Z",
):
    return Job(
        company=company,
        position=position,
        location=location,
        apply_url=url,
        post_date=posted[:10],
        posted_at=posted,
        valid_through="2027-01-01",
        sponsorship_evidence=evidence,
        sponsorship_quote="",
        visa="Visa sponsorship",
        reloc=reloc,
        contract="",
        source="test",
        link_status="alive",
        summary="",
        salary=salary,
    )


class TemplateTests(unittest.TestCase):
    def test_telegram_reads_as_a_short_block_and_hides_the_address(self):
        role = job(
            "Applied AI Engineer",
            company="A&B <Labs>",
            location="San Francisco, CA, United States",
            salary={"currency": "USD", "min": 280000, "max": 320000, "unit": "YEAR"},
            reloc="Relocation assistance",
            url="https://job-boards.greenhouse.io/anthropic/jobs/5483945008",
        )
        other = job(
            "Brand Designer",
            company="Monzo",
            location="London, United Kingdom",
            evidence="likely",
            url="https://job-boards.greenhouse.io/monzo/jobs/1",
            posted="2026-11-18T09:00:00Z",
        )
        html = render_telegram([role, other], THURSDAY)
        preview = render_telegram_preview([role, other], THURSDAY)
        self.assertIn("<b>Visa-sponsored roles</b>\nThu 19 Nov", html)
        self.assertIn("🇺🇸 <b>Applied AI Engineer</b>", html)
        self.assertIn("A&amp;B &lt;Labs&gt;", html)
        self.assertIn("San Francisco, United States", html)
        self.assertIn("$280k–$320k", html)
        self.assertIn("✅ Visa sponsorship confirmed", html)
        self.assertIn("✈️ Relocation support", html)
        self.assertIn(">View &amp; apply</a>", html)
        self.assertIn("visajobs.xyz/visa-sponsored-jobs", html)
        self.assertIn("Share with a friend who wants to move abroad.", html)
        self.assertIn("Visa sponsorship likely", html)
        self.assertNotIn("✅ Visa sponsorship likely", preview)
        self.assertNotIn("http", preview)
        self.assertNotIn("<b>", preview)
        self.assertNotIn("<a", preview)
        self.assertIn("A&B <Labs>", preview)
        self.assertIn("\n\n🇺🇸 Applied AI Engineer\n", preview)
        self.assertLess(html.index("Applied AI Engineer"), html.index("Brand Designer"))
        # A blank line sits between the two roles.
        self.assertIn("View & apply\n\n🇬🇧 Brand Designer", preview)
        linkedin = render_linkedin([role], THURSDAY)
        self.assertIn("View & apply: https://visajobs.xyz/visa-sponsored-jobs/", linkedin)
        self.assertIn("#visasponsorship #relocation #techjobs #hiring", linkedin)
        self.assertNotIn("<b>", linkedin)
        self.assertNotIn("confirmed", html.lower().split("visa sponsorship confirmed")[0])

    def test_salary_keeps_an_uneven_range(self):
        text = render_telegram_preview(
            [job("Analyst", salary={"currency": "GBP", "min": 56100, "max": 64000, "unit": "YEAR"})],
            THURSDAY,
        )
        self.assertIn("£56,100–£64,000", text)


class RankingTests(unittest.TestCase):
    def test_best_roles_come_first_and_the_digest_stops_at_five(self):
        roles = [
            job("Old confirmed", url="https://co.example/old", posted="2026-11-01T00:00:00Z"),
            job("New confirmed", url="https://co.example/new", posted="2026-11-19T00:00:00Z"),
            job("Paid likely", evidence="likely", salary={"currency": "EUR", "min": 80000, "max": 90000, "unit": "YEAR"}, url="https://co.example/paid"),
            job("Direct confirmed", url="https://boards.greenhouse.io/acme/jobs/9", posted="2026-11-10T00:00:00Z"),
            job("Aggregator", url="https://www.linkedin.com/jobs/view/9", posted="2026-11-19T08:00:00Z"),
            job("Sixth", url="https://co.example/six", posted="2026-11-18T00:00:00Z"),
            job("With salary", salary={"currency": "EUR", "min": 100000, "max": 120000, "unit": "YEAR"}, url="https://co.example/salary", posted="2026-11-02T00:00:00Z"),
        ]
        picked = [item.position for item in select_roles(roles)]
        self.assertEqual(
            picked,
            ["With salary", "New confirmed", "Sixth", "Direct confirmed", "Old confirmed"],
        )
        self.assertNotIn("Paid likely", picked)
        self.assertNotIn("Aggregator", picked)

    def test_digest_does_not_let_one_employer_take_every_slot(self):
        roles = []
        for index, company in enumerate(("Anthropic", "Picnic", "N26", "PayPay")):
            for slot in range(3):
                roles.append(
                    job(
                        f"{company} {slot}",
                        company=company,
                        url=f"https://jobs.example.com/{company}/{slot}",
                        posted=f"2026-11-{10+index:02d}T0{slot}:00:00Z",
                    )
                )
        picked = select_roles(roles)
        companies = [item.company for item in picked]
        self.assertEqual(len(picked), 5)
        self.assertLessEqual(companies.count("Anthropic"), 2)
        self.assertGreaterEqual(len(set(companies)), 3)

    def test_linkedin_commentary_escapes_markup_and_org_id_is_digits(self):
        self.assertEqual(linkedin_commentary("Role (remote)"), r"Role \(remote\)")
        self.assertEqual(organization_id("urn:li:organization:90907794"), "90907794")
        self.assertEqual(organization_id("90907794"), "90907794")


class DeliveryTests(unittest.TestCase):
    def test_one_digest_a_day_records_ids_and_keeps_the_rest(self):
        roles = [job(f"Role {index}", url=f"https://co.example/{index}", posted=f"2026-11-{10+index:02d}T00:00:00Z") for index in range(1, 7)]
        sent = {"telegram": [], "linkedin": []}
        path = Path(self.id().replace(".", "_") + "-posted.json")
        # Keep the ledger next to the test file's temp via the home of this process.
        path = Path("/tmp") / path.name

        def telegram(text, on):
            sent["telegram"].append(text)

        def linkedin(text):
            sent["linkedin"].append(text)

        announce(roles, roles, today=THURSDAY, ledger_path=path, telegram_send=telegram, linkedin_send=linkedin)
        self.assertEqual(len(sent["telegram"]), 1)
        self.assertEqual(len(sent["linkedin"]), 1)
        self.assertEqual(sent["telegram"][0].count("View &amp; apply"), 5)
        announce(roles, [], today=THURSDAY, ledger_path=path, telegram_send=telegram, linkedin_send=linkedin)
        self.assertEqual(len(sent["telegram"]), 1)
        announce(roles, [], today=date(2026, 11, 20), ledger_path=path, telegram_send=telegram, linkedin_send=linkedin)
        self.assertEqual(len(sent["telegram"]), 2)
        self.assertIn("Role 1", sent["telegram"][1])
        self.assertNotIn("Role 6", sent["telegram"][1])
        posted = path.read_text(encoding="utf-8")
        self.assertIn(canonical_url("https://co.example/6"), posted)
        path.unlink(missing_ok=True)

    def test_dry_run_prints_without_sending_or_recording(self):
        role = job("Only role", url="https://co.example/only")
        path = Path("/tmp/dry-run-posted.json")
        path.unlink(missing_ok=True)
        calls = []
        announce(
            [role],
            [role],
            today=THURSDAY,
            dry_run=True,
            ledger_path=path,
            telegram_send=lambda text, on: calls.append(text),
            linkedin_send=lambda text: calls.append(text),
        )
        self.assertEqual(calls, [])
        self.assertFalse(path.exists())

    def test_nothing_new_does_not_post(self):
        role = job("Already", url="https://co.example/done")
        path = Path("/tmp/nothing-new-posted.json")
        ident = job_id(role)
        path.write_text(
            '{"posted": {"telegram": ["%s"], "linkedin": ["%s"]}, "pending": [], "last_post": {"telegram": "", "linkedin": ""}}\n'
            % (ident, ident),
            encoding="utf-8",
        )
        calls = []
        announce([role], [], today=THURSDAY, ledger_path=path, telegram_send=lambda text, on: calls.append("t"), linkedin_send=lambda text: calls.append("l"))
        self.assertEqual(calls, [])
        path.unlink(missing_ok=True)

    def test_weekend_telegram_is_silent(self):
        self.assertEqual(telegram_fields("hi", SATURDAY, "@visa")["disable_notification"], "true")
        self.assertEqual(telegram_fields("hi", THURSDAY, "@visa")["disable_notification"], "false")
        self.assertEqual(telegram_fields("hi", THURSDAY, "@visa")["disable_web_page_preview"], "true")


if __name__ == "__main__":
    unittest.main()
