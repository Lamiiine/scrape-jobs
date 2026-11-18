import unittest

from scraper.classify import classify, excerpt, html_to_text, opening_excerpt


class ClassifyTests(unittest.TestCase):
    def test_monzo_phrase_is_confirmed(self):
        text = "Benefits. We can sponsor visas. We can help you relocate to the UK."
        result = classify(text, company="Monzo")
        self.assertEqual(result.level, "confirmed")
        self.assertIn("sponsor", result.quote.lower())
        self.assertTrue(result.relocation)

    def test_anthropic_offer_survives_the_caveat_sentence(self):
        text = (
            "Visa sponsorship: We do sponsor visas! "
            "However, we aren't able to successfully sponsor visas for every role and every candidate. "
            "But if we make you an offer, we will make every reasonable effort to get you a visa."
        )
        result = classify(text, company="Anthropic")
        self.assertEqual(result.level, "confirmed")
        self.assertIn("We do sponsor visas", result.quote)

    def test_explicit_refusal_is_unverified(self):
        text = "Visa sponsorship is NOT provided for this position."
        result = classify(text, company="Cloudflare")
        self.assertEqual(result.level, "unverified")
        self.assertFalse(result.publish)

    def test_work_authorization_refusal(self):
        text = "You must be work authorized in the United States without the need for new visa sponsorship."
        result = classify(text, company="Adyen", known_sponsors={"adyen"})
        self.assertEqual(result.level, "unverified")

    def test_false_friends(self):
        self.assertEqual(classify("Own a product that requires C-suite sponsorship.").level, "unverified")
        self.assertEqual(classify("Act as a key executive sponsor for startups.").level, "unverified")
        self.assertEqual(classify("Experience with sponsored media and advertising.").level, "unverified")

    def test_n26_package_confirms_visa_and_relocation(self):
        text = "A relocation package with visa support for those who need it."
        result = classify(text, company="N26")
        self.assertEqual(result.level, "confirmed")
        self.assertTrue(result.relocation)

    def test_willing_to_relocate_is_not_assistance(self):
        text = "We do sponsor visas. You must be willing to relocate to Amsterdam."
        result = classify(text)
        self.assertEqual(result.level, "confirmed")
        self.assertFalse(result.relocation)

    def test_known_sponsor_without_text_is_likely(self):
        result = classify("Backend engineer in London.", company="Monzo", known_sponsors={"monzo"})
        self.assertEqual(result.level, "likely")
        self.assertIn("known-sponsor", result.quote)

    def test_greenhouse_escaped_html_keeps_paragraphs_and_the_offer(self):
        raw = (
            "&lt;h2&gt;About&lt;/h2&gt;&lt;p&gt;Visa sponsorship:&amp;nbsp;We do sponsor visas!&lt;/p&gt;"
            "&lt;p&gt;However, we aren't able to successfully sponsor visas for every role.&lt;/p&gt;"
        )
        text = html_to_text(raw)
        self.assertNotIn("&lt;", text)
        self.assertNotIn("&nbsp;", text)
        self.assertIn("\n", text)
        self.assertIn("We do sponsor visas", text)
        result = classify(raw, company="Anthropic")
        self.assertEqual(result.level, "confirmed")
        self.assertIn("We do sponsor visas", result.quote)
        self.assertLessEqual(len(excerpt(text, limit=40)), 41)
        card = opening_excerpt("About Anthropic\n\nMission statement that is boilerplate.\n\nAbout the role\n\nAs an engineer you will advise customers.")
        self.assertTrue(card.startswith("As an engineer"))

    def test_known_sponsor_refusal_is_not_likely(self):
        result = classify(
            "Visa sponsorship is not available for this role.",
            company="Monzo",
            known_sponsors={"monzo"},
        )
        self.assertEqual(result.level, "unverified")


if __name__ == "__main__":
    unittest.main()
