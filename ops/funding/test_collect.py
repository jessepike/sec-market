import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import collect  # noqa: E402

POST = (Path(__file__).parent / "fixtures" / "post-excerpt.html").read_text()


class ParseTest(unittest.TestCase):
    def setUp(self):
        self.rounds = collect.parse_rounds(collect.funding_section(POST))

    def test_week_and_section(self):
        self.assertEqual(collect.parse_week(POST), "2026-10-26")
        self.assertNotIn("Scopertos", collect.funding_section(POST))

    def test_rounds(self):
        got = [(r["company"], r["amountUsd"], r["stage"], r["lead"]) for r in self.rounds]
        self.assertEqual(got, [
            ("&Truth", 70_000_000, "Seed", None),
            ("Infisical", 40_000_000, "Series B", "Elad Gil"),
            ("ARMS Cyber", 10_000_000, "Venture round", None),
            ("BlackWall (formerly BotGuard)", 100_000_000, "Series C", "AVP"),
            ("Mave", 28_000_000, "Series A", "Red Dot Capital Partners, Dell Technologies Capital, and Emerge Ventures"),
            ("Mave", 6_000_000, "Seed", "Red Dot Capital Partners, Dell Technologies Capital, and Emerge Ventures"),
            ("AvalonX", None, "Venture round", "Ridown Capital"),
        ])
        self.assertEqual(self.rounds[1]["sourceUrl"], "https://infisical.com/blog/series-b")
        self.assertEqual(self.rounds[1]["companyUrl"], "http://www.infisical.com")

    def test_archive_links(self):
        html = '<a href="/p/security-funded-267">x</a><a href="https://www.returnonsecurity.com/p/security-funded-268">y</a><a href="/p/other">z</a>'
        self.assertEqual([n for n, _ in collect.post_links(html)], [268, 267])


class ConfirmTest(unittest.TestCase):
    r = {"company": "Infisical", "amountUsd": 40_000_000, "stage": "Series B"}

    def test_amount_forms(self):
        for text in ["Infisical raises $40 million Series B", "Infisical closes $40M round", "Infisical: $40.0M led by Elad Gil"]:
            self.assertTrue(collect.confirm(self.r, text)[0], text)

    def test_missing_amount_or_name(self):
        self.assertFalse(collect.confirm(self.r, "Infisical raises a Series B")[0])
        self.assertFalse(collect.confirm(self.r, "Another company raises $40 million")[0])
        # A longer word containing the name does not count.
        self.assertFalse(collect.confirm({"company": "Arms", "amountUsd": 10_000_000, "stage": "Seed"}, "Farmsco raises $10 million")[0])

    def test_name_variants(self):
        bw = {"company": "BlackWall (formerly BotGuard)", "amountUsd": 100_000_000, "stage": "Series C"}
        self.assertTrue(collect.confirm(bw, "BlackWall raises $100 million at $2.2 billion valuation")[0])
        mo = {"company": "Modelyo Technologies", "amountUsd": 17_000_000, "stage": "Venture round"}
        self.assertTrue(collect.confirm(mo, "Modelyo raised $17 million")[0])

    def test_undisclosed_is_held(self):
        r = {"company": "AvalonX", "amountUsd": None, "stage": "Venture round"}
        self.assertFalse(collect.confirm(r, "AvalonX announces venture funding")[0])

    def test_form_d(self):
        r = {"company": "ARMS Cyber", "amountUsd": 10_000_000, "stage": "Venture round"}
        self.assertTrue(collect.confirm_form_d(r, "<issuerName>ARMS Cyber, Inc.</issuerName><totalAmountSold>$10,000,000</totalAmountSold>")[0])
        self.assertFalse(collect.confirm_form_d(r, "<issuerName>ARMS Cyber, Inc.</issuerName><totalAmountSold>$4,000,000</totalAmountSold>")[0])


class PortfolioTest(unittest.TestCase):
    def test_names_and_skip(self):
        html = '<a href="https://forgepointcap.com/companies/1kosmos/">a</a><a href="https://forgepointcap.com/companies/huntress/case-study">b</a><a href="https://forgepointcap.com/companies/page/2/">n</a>'
        pat = collect.PORTFOLIOS[1]["pattern"]
        self.assertEqual(collect.portfolio_names(html, pat), ["1kosmos"])


if __name__ == "__main__":
    unittest.main()
