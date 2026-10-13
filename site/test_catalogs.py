import json
from html.parser import HTMLParser
import re
import unittest
from unittest.mock import patch
from tempfile import TemporaryDirectory
from pathlib import Path

import build_catalogs


SITE = Path(__file__).resolve().parent


class CatalogTests(unittest.TestCase):
    def test_starter_links_resolve_to_shipped_files(self):
        class Links(HTMLParser):
            def __init__(self):
                super().__init__()
                self.hrefs = []

            def handle_starttag(self, tag, attrs):
                if tag == "a":
                    self.hrefs.extend(value for key, value in attrs if key == "href")

        links = Links()
        links.feed((SITE / "start.html").read_text(encoding="utf-8"))
        for href in links.hrefs:
            if href.startswith("#"):
                continue
            if href.startswith("https://github.com/The-825/breadcrumbs/"):
                relative = href.split("/main/", 1)[1]
                target = SITE.parent / relative
            elif href.startswith("https://"):
                continue
            else:
                target = SITE / href
            self.assertTrue(target.exists(), href)
        self.assertIn('href="start.html"', (SITE / "index.html").read_text(encoding="utf-8"))

    @classmethod
    def setUpClass(cls):
        cls.research = json.loads((SITE / "data" / "research.json").read_text(encoding="utf-8"))
        cls.repositories = json.loads((SITE / "data" / "repositories.json").read_text(encoding="utf-8"))
        cls.claims = json.loads((SITE / "data" / "claims.json").read_text(encoding="utf-8"))

    def test_all_reviewed_records_are_present(self):
        ledger = (SITE.parent / "docs" / "collaborative-intelligence-research-ledger.md").read_text(encoding="utf-8")
        source_ids = re.findall(r"^\| ((?:[0-9]{3}|C-[0-9]{3})) \|", ledger, re.MULTILINE)
        landscape = json.loads((SITE.parent / "docs" / "collaborative-intelligence-repository-landscape.json").read_text(encoding="utf-8"))
        repository_ids = [item["id"] for item in landscape["repositories"]]
        self.assertLessEqual(set(source_ids), {item["id"] for item in self.research})
        self.assertLessEqual(set(repository_ids), {item["id"] for item in self.repositories})
        self.assertEqual(len({item['id'] for item in self.research}), len(self.research))
        self.assertEqual(len({item['id'] for item in self.repositories}), len(self.repositories))
        self.assertEqual(17, len(self.claims))

    def test_orch_remains_a_bounded_candidate(self):
        ledger = (SITE.parent / "docs" / "collaborative-intelligence-research-ledger.md").read_text(encoding="utf-8")
        appraisals = (SITE.parent / "docs" / "collaborative-intelligence-source-appraisals.md").read_text(encoding="utf-8")
        self.assertIn("https://arxiv.org/abs/2609.11737", ledger)
        self.assertIn("| C-001 |", ledger)
        self.assertIn("not promoted or adopted", ledger)
        self.assertIn("claims not validated", appraisals)
        candidate = next(item for item in self.research if item['id'] == 'C-001')
        self.assertEqual('candidate-not-promoted', candidate['record_state'])
        self.assertIn('https://arxiv.org/abs/2609.11737', candidate['url'])

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
            if item["stars_observed"] is None:
                self.assertIsNone(item["starsObservedDate"])
            else:
                self.assertTrue(item["starsObservedDate"])
            self.assertNotIn("score", item)

    def test_popularity_uses_observed_cohort_and_its_own_date(self):
        def record(identity, stars, **extra):
            return dict(id=identity, repository=f"example/{identity}",
                        evidence_depth="readme-screened", stars_observed=stars,
                        category="research-framework", mechanisms={"memory_context": "U"},
                        claims=[], snapshot_date="2026-10-07", **extra)

        data = dict(popularity_observed_date="2026-08-27", repositories=[
            record("A", 10, popularity_observed_date="2026-09-01"),
            record("B", None), record("C", 0),
        ])
        with TemporaryDirectory() as directory:
            docs = Path(directory)
            (docs / "collaborative-intelligence-repository-landscape.json").write_text(
                json.dumps(data), encoding="utf-8")
            with patch.object(build_catalogs, "DOCS", docs):
                rows = build_catalogs.repository_catalog()
        self.assertEqual(["A", "C", "B"], [row["id"] for row in rows])
        self.assertEqual([1, 2, None], [row["popularityOrder"] for row in rows])
        self.assertEqual([1, 2, None], [row["categoryPopularityOrder"] for row in rows])
        self.assertTrue(all(row["popularityCount"] == 2 for row in rows))
        self.assertTrue(all(row["categoryPopularityCount"] == 2 for row in rows))
        self.assertTrue(all(row["detailedReviewCount"] == 3 for row in rows))
        self.assertEqual(["2026-09-01", "2026-08-27", None],
                         [row["starsObservedDate"] for row in rows])

    def test_portable_assessments_do_not_fake_popularity_or_mechanism_review(self):
        portable = [item for item in self.repositories if item["evidence_depth"] == "source-assessment"]
        self.assertTrue(portable)
        for item in portable:
            self.assertIsNone(item["stars_observed"])
            self.assertIsNone(item["popularityOrder"])
            self.assertEqual(item["unknownMechanisms"], item["mechanismTotal"])

    def test_detailed_repository_review_count_exceeds_original_saturation_baseline(self):
        depths = {item["evidence_depth"] for item in self.repositories}
        self.assertEqual({"readme-screened", "source-assessment"}, depths)
        detailed = [item for item in self.repositories if item["evidence_depth"] == "readme-screened"]
        portable = [item for item in self.repositories if item["evidence_depth"] == "source-assessment"]
        self.assertEqual(len(self.repositories), len(detailed) + len(portable))
        self.assertTrue(all(item["detailedReviewCount"] == len(detailed) for item in self.repositories))
        self.assertGreater(len(detailed), 100)

    def test_home_catalog_counts_load_from_data(self):
        home = (SITE / "index.html").read_text(encoding="utf-8")
        script = (SITE / "home.js").read_text(encoding="utf-8")
        llms = (SITE.parent / "llms.txt").read_text(encoding="utf-8")
        self.assertIn('id="research-total">Loading</div>', home)
        self.assertIn('id="repository-total">Loading</div>', home)
        self.assertIn('src="home.js?v=', home)
        self.assertIn('readCatalog("research")', script)
        self.assertIn('readCatalog("repositories")', script)
        self.assertIn('item.evidence_depth === "readme-screened"', script)
        self.assertIn('item.evidence_depth === "source-assessment"', script)
        self.assertNotIn("311-repository ledger", llms)

    def test_table_headers_do_not_float_over_rows(self):
        css = (SITE / "app.css").read_text(encoding="utf-8")
        self.assertIn("th { position: static;", css)

    def test_research_identity_and_order_are_separate(self):
        page = (SITE / "research.html").read_text(encoding="utf-8")
        script = (SITE / "app.js").read_text(encoding="utf-8")
        self.assertIn("<th>Review number</th><th>Evidence order</th><th>Source</th>", page)
        self.assertIn('${escapeHtml(item.id)}</td>', script)
        self.assertIn('${item.evidenceOrder}<small> / ${items.length}</small>', script)
        self.assertIn('${item.evidenceOrder} / ${all.length}', (SITE / "detail.js").read_text(encoding="utf-8"))
        self.assertNotIn("100 reviewed sources", page)
        self.assertNotIn("0 of 100", page)
        self.assertNotIn('${item.id}. ${item.title}', script)

    def test_public_profiles_include_visual_explanations(self):
        jarvis = (SITE / "jarvis.html").read_text(encoding="utf-8")
        detail = (SITE / "detail.js").read_text(encoding="utf-8")
        self.assertIn('class="system-map"', jarvis)
        self.assertIn("Mechanism profile", detail)
        self.assertIn("Last reviewed", detail)

    def test_every_page_has_accessible_navigation(self):
        for name in ("index.html", "start.html", "research.html", "repositories.html", "detail.html", "jarvis.html", "claims.html", "methodology.html", "papers.html", "synthesis.html"):
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
        self.assertIn('href="https://the-825.github.io/staletoast/synthesis.html"', index)
        self.assertIn('href="https://the-825.github.io/staletoast/synthesis.html"', research)
        self.assertIn("five evidence trails", synthesis.lower())
        self.assertIn('href="https://the-825.github.io/staletoast/claims.html#ci-017"', synthesis)
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
