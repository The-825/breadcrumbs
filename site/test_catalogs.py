import json
import unittest
from pathlib import Path


SITE = Path(__file__).resolve().parent


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.research = json.loads((SITE / "data" / "research.json").read_text(encoding="utf-8"))
        cls.repositories = json.loads((SITE / "data" / "repositories.json").read_text(encoding="utf-8"))
        cls.claims = json.loads((SITE / "data" / "claims.json").read_text(encoding="utf-8"))

    def test_all_reviewed_records_are_present(self):
        self.assertEqual(100, len(self.research))
        self.assertEqual(314, len(self.repositories))
        self.assertEqual(100, len({item["id"] for item in self.research}))
        self.assertEqual(314, len({item["id"] for item in self.repositories}))
        self.assertEqual(17, len(self.claims))

    def test_profiles_keep_signals_separate(self):
        for item in self.research:
            self.assertIn(item["directness"][:2], {"D0", "D1", "D2", "D3"})
            self.assertIn(item["directnessValue"], range(4))
            self.assertIn(item["horizonValue"], range(4))
            self.assertTrue(item["familyLabel"])
            self.assertEqual(len(item["claims"]), item["claimCount"])
            self.assertEqual("not collected", item["citationSignal"])
            self.assertTrue(item["claims"])
            self.assertNotIn("score", item)
        for item in self.repositories:
            self.assertIn("stars_observed", item)
            self.assertIn("evidence_depth", item)
            self.assertIn("mechanisms", item)
            if item["categoryPopularityOrder"] is not None:
                self.assertLessEqual(item["categoryPopularityOrder"], item["categoryRepositoryCount"])
            self.assertEqual(item["mechanismTotal"], len(item["mechanisms"]))
            self.assertEqual(item["claimCount"], len(item["claims"]))
            self.assertEqual(item["unknownMechanisms"], sum(value == "U" for value in item["mechanisms"].values()))
            self.assertEqual(item["snapshot_date"], item["lastReviewed"])
            self.assertTrue(item["starsObservedDate"])
            self.assertNotIn("score", item)

    def test_portable_assessments_do_not_fake_popularity_or_mechanism_review(self):
        portable = [item for item in self.repositories if item["evidence_depth"] == "source-assessment"]
        self.assertEqual(214, len(portable))
        for item in portable:
            self.assertIsNone(item["stars_observed"])
            self.assertIsNone(item["popularityOrder"])
            self.assertEqual(item["unknownMechanisms"], item["mechanismTotal"])

    def test_table_headers_do_not_float_over_rows(self):
        css = (SITE / "app.css").read_text(encoding="utf-8")
        self.assertIn("th { position: static;", css)

    def test_research_identity_and_order_are_separate(self):
        page = (SITE / "research.html").read_text(encoding="utf-8")
        script = (SITE / "app.js").read_text(encoding="utf-8")
        self.assertIn("<th>Review number</th><th>Evidence order</th><th>Source</th>", page)
        self.assertIn('${escapeHtml(item.id)}</td>', script)
        self.assertIn('${item.evidenceOrder}<small> / 100</small>', script)
        self.assertNotIn('${item.id}. ${item.title}', script)

    def test_public_profiles_include_visual_explanations(self):
        jarvis = (SITE / "jarvis.html").read_text(encoding="utf-8")
        detail = (SITE / "detail.js").read_text(encoding="utf-8")
        self.assertIn('class="system-map"', jarvis)
        self.assertIn("Mechanism profile", detail)
        self.assertIn("Last reviewed", detail)

    def test_every_page_has_accessible_navigation(self):
        for name in ("index.html", "research.html", "repositories.html", "detail.html", "jarvis.html", "claims.html", "methodology.html", "papers.html", "synthesis.html"):
            page = (SITE / name).read_text(encoding="utf-8")
            self.assertIn('href="#main"', page)
            self.assertIn('aria-label="Primary"', page)
            self.assertIn('href="app.css?v=', page)

    def test_white_paper_and_synthesis_are_publicly_routed(self):
        index = (SITE / "index.html").read_text(encoding="utf-8")
        research = (SITE / "research.html").read_text(encoding="utf-8")
        papers = (SITE / "papers.html").read_text(encoding="utf-8")
        synthesis = (SITE / "synthesis.html").read_text(encoding="utf-8")
        self.assertIn("Read the White Paper", index)
        self.assertIn("breadcrumbs-whitepaper.md", papers)
        self.assertIn('href="synthesis.html"', index)
        self.assertIn('href="synthesis.html"', research)
        self.assertIn("five evidence trails", synthesis.lower())
        self.assertIn("CI-017", synthesis)
        self.assertIn("Evidence boundary", synthesis)
        for page in (index, research, papers, synthesis):
            self.assertIn("Community</a>", page)
        repositories = (SITE / "repositories.html").read_text(encoding="utf-8")
        for page in (index, research, repositories, papers, synthesis):
            for trail in ("Research", "Synthesis", "Repositories", "Claims", "Papers", "Method", "Jarvis", "Community"):
                self.assertIn(f">{trail}</a>", page)

    def test_every_page_exposes_the_complete_trail_set(self):
        trails = ("Research", "Synthesis", "Repositories", "Claims", "Papers", "Method", "Jarvis", "Community")
        for name in ("index.html", "research.html", "repositories.html", "detail.html", "jarvis.html", "claims.html", "methodology.html", "papers.html", "synthesis.html"):
            page = (SITE / name).read_text(encoding="utf-8")
            for trail in trails:
                self.assertIn(f">{trail}</a>", page, f"{name} is missing {trail}")

    def test_no_private_runtime_language(self):
        public_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in SITE.rglob("*")
            if path.is_file() and path.suffix in {".html", ".css", ".js", ".json"}
        ).lower()
        for blocked in ("student record", "ferpa record", "jarvis token", "operator dashboard token"):
            self.assertNotIn(blocked, public_text)


if __name__ == "__main__":
    unittest.main()
