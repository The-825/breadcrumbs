import json
import os
import re
import unittest


_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_REGISTER = os.path.join(_REPO, "docs", "collaborative-intelligence-repository-landscape.json")


class TestRepositoryLandscape(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(_REGISTER, encoding="utf-8") as handle:
            cls.data = json.load(handle)

    def test_cohort_is_unique_and_pinned(self):
        rows = self.data["repositories"]
        self.assertEqual(len(rows), 206)
        self.assertEqual(len({row["id"] for row in rows}), len(rows))
        self.assertEqual(len({row["repository"].lower() for row in rows}), len(rows))
        for row in rows:
            self.assertRegex(row["id"], r"^R-\d{3}$")
            if row["evidence_depth"] == "source-assessment":
                self.assertIsNone(row["snapshot_commit"])
                self.assertIsNone(row["stars_observed"])
                self.assertEqual(set(row["mechanisms"].values()), {"U"})
            else:
                self.assertRegex(row["snapshot_commit"], r"^[0-9a-f]{40}$")
                # A genuinely unstarred repository (0) is real, sourced data, not a
                # sentinel; only a negative or missing value would be a bug.
                self.assertGreaterEqual(row["stars_observed"], 0)
            self.assertRegex(row["snapshot_date"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertEqual(row["url"], f"https://github.com/{row['repository']}")
            self.assertTrue(row["selection_aspect"])

    def test_mechanism_profiles_are_complete_without_scores(self):
        dimensions = self.data["dimensions"]
        allowed = set(self.data["status_codes"])
        self.assertEqual(len(dimensions), len(set(dimensions)))
        for row in self.data["repositories"]:
            with self.subTest(repository=row["repository"]):
                self.assertEqual(set(row["mechanisms"]), set(dimensions))
                self.assertTrue(set(row["mechanisms"].values()) <= allowed)
                self.assertNotIn("score", row)
                self.assertNotIn("rank", row)

    def test_claim_links_use_method_v2_ids(self):
        for row in self.data["repositories"]:
            if row["evidence_depth"] != "source-assessment":
                self.assertTrue(row["claims"])
            for claim in row["claims"]:
                match = re.fullmatch(r"CI-(\d{3})", claim)
                self.assertIsNotNone(match)
                self.assertIn(int(match.group(1)), range(1, 18))

    def test_wave_does_not_overstate_depth_or_lifecycle(self):
        allowed_lifecycle = {"current", "maintenance", "research-artifact", "unknown"}
        for row in self.data["repositories"]:
            self.assertIn(row["lifecycle"], allowed_lifecycle)
            self.assertIn(row["evidence_depth"], {"readme-screened", "source-assessment"})
            if row["evidence_depth"] == "readme-screened":
                self.assertIn(row["evidence_pointer"], {"README.md", "README.MD"})
        maintenance = [row["repository"] for row in self.data["repositories"] if row["lifecycle"] == "maintenance"]
        self.assertEqual(maintenance, ["microsoft/graphrag", "microsoft/autogen"])

    def test_expansion_is_aspect_balanced_and_tracks_research_artifacts(self):
        rows = self.data["repositories"]
        categories = {row["category"] for row in rows}
        self.assertIn("model-gateway", categories)
        self.assertIn("execution-sandbox", categories)
        self.assertGreaterEqual(len(categories), 10)
        artifacts = [row for row in rows if row["lifecycle"] == "research-artifact"]
        self.assertGreaterEqual(len(artifacts), 4)
        self.assertTrue(all(row["category"] == "research-framework" for row in artifacts))

    def test_popularity_is_dated_and_not_a_score(self):
        self.assertEqual(self.data["popularity_observed_date"], "2026-08-27")
        self.assertIn("not a quality score", self.data["popularity_boundary"])

    def test_public_transfer_is_deduplicated_and_non_authorizing(self):
        summary = self.data["import_summary"]
        self.assertEqual(summary["transfer_record_count"], 224)
        self.assertEqual(summary["assessment_source_count"], 226)
        self.assertEqual(summary["unique_resolved_transfer_repositories"], 224)
        self.assertEqual(summary["overlap_collapsed"], 10)
        self.assertEqual(summary["new_repositories_imported"], 214)
        self.assertEqual(summary["unique_repository_count_after"], 314)
        self.assertEqual(summary["transfer_duplicate_collapse_count"], 2)
        self.assertEqual(summary["unresolved_identity_count"], 0)
        self.assertEqual(summary["unresolved_identity_count_excluded"], 4)
        self.assertEqual(summary["supporting_reference_repository_count_excluded"], 19)
        self.assertEqual(summary["excluded_portfolio_repository_count"], 9)
        self.assertEqual(summary["license_unknown_count"], 312)
        self.assertEqual(summary["upstream_revision_unknown_count"], 212)
        self.assertEqual(summary["authority"], "descriptive-only")
        self.assertRegex(summary["transfer_upstream_revision"], r"^[0-9a-f]{40}$")
        self.assertNotIn("operated_repositories", self.data)
        for row in self.data["repositories"]:
            for source in row.get("portable_assessments", []):
                self.assertEqual(source["authority"], "evidence-only")
                self.assertTrue(source["source_links"])
                self.assertTrue(source["repository_stable_id"])
                self.assertTrue(source["assessment_artifact_ids"])
                self.assertNotIn("source_path", source)

    def test_unresolved_identities_are_excluded_from_public_ledger(self):
        rows = self.data["unresolved_identities"]
        self.assertEqual(rows, [])

    def test_wave_r4_promotions_carry_their_own_observation_date(self):
        # Wave R4 reviewed the D-44 transfer's 214 unscreened repositories on a later
        # date than the original 100-repository popularity sweep. A promoted record
        # must carry its own stars_observed_date instead of silently inheriting the
        # global popularity_observed_date for stars nobody re-observed on that date.
        global_date = self.data["popularity_observed_date"]
        dated = [row for row in self.data["repositories"] if row.get("stars_observed_date")]
        self.assertGreater(len(dated), 0)
        for row in dated:
            self.assertRegex(row["stars_observed_date"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertNotEqual(row["stars_observed_date"], global_date)


if __name__ == "__main__":
    unittest.main()
