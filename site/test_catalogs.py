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
        self.assertEqual(100, len(self.repositories))
        self.assertEqual(100, len({item["id"] for item in self.research}))
        self.assertEqual(100, len({item["id"] for item in self.repositories}))
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
            self.assertLessEqual(item["categoryPopularityOrder"], item["categoryRepositoryCount"])
            self.assertEqual(item["mechanismTotal"], len(item["mechanisms"]))
            self.assertEqual(item["claimCount"], len(item["claims"]))
            self.assertEqual(item["snapshot_date"], item["lastReviewed"])
            self.assertTrue(item["starsObservedDate"])
            self.assertNotIn("score", item)

    def test_table_headers_do_not_float_over_rows(self):
        css = (SITE / "app.css").read_text(encoding="utf-8")
        self.assertIn("th { position: static;", css)

    def test_public_profiles_include_visual_explanations(self):
        jarvis = (SITE / "jarvis.html").read_text(encoding="utf-8")
        detail = (SITE / "detail.js").read_text(encoding="utf-8")
        self.assertIn('class="system-map"', jarvis)
        self.assertIn("Mechanism profile", detail)
        self.assertIn("Last reviewed", detail)

    def test_every_page_has_accessible_navigation(self):
        for name in ("index.html", "research.html", "repositories.html", "detail.html", "jarvis.html", "claims.html", "methodology.html"):
            page = (SITE / name).read_text(encoding="utf-8")
            self.assertIn('href="#main"', page)
            self.assertIn('aria-label="Primary"', page)
            self.assertIn('href="app.css?v=', page)

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
