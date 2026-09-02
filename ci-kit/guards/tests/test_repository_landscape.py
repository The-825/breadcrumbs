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
        self.assertEqual(len(rows), 311)
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
                self.assertGreaterEqual(row["stars_observed"], 0)
            self.assertRegex(row["snapshot_date"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertEqual(row["url"], f"https://github.com/{row['repository']}")
            self.assertTrue(row["selection_aspect"])

    def test_review_wave_expands_depth_without_shrinking_portable_ledger(self):
        rows = self.data["repositories"]
        detailed = [row for row in rows if row["evidence_depth"] == "readme-screened"]
        portable = [row for row in rows if row["evidence_depth"] == "source-assessment"]
        promoted = [row for row in detailed if row.get("detailed_review", {}).get("wave") == "R4"]
        self.assertEqual(206, len(detailed))
        self.assertEqual(105, len(portable))
        self.assertEqual(106, len(promoted))
        self.assertTrue(all(row.get("portable_assessments") for row in promoted))
        self.assertTrue(all(row["detailed_review"]["authority"] == "descriptive-only" for row in promoted))
        self.assertEqual(206, self.data["review_summary"]["detailed_appraisal_count"])
        self.assertEqual(105, self.data["review_summary"]["portable_only_count"])
        self.assertEqual(311, self.data["review_summary"]["total_repository_count"])
        self.assertEqual(105, self.data["review_summary"]["portable_only_triaged_count"])
        self.assertTrue(all(row.get("detailed_review_triage", {}).get("status") == "screened-not-promoted" for row in portable))
        self.assertTrue(all(row["detailed_review_triage"]["authority"] == "descriptive-only" for row in portable))

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
        self.assertEqual(summary["producer_contract_version"], "2.0")
        self.assertEqual(summary["transfer_record_count"], 223)
        self.assertEqual(summary["assessment_source_count"], 225)
        self.assertEqual(summary["unique_resolved_transfer_repositories"], 223)
        self.assertEqual(summary["overlap_collapsed"], 12)
        self.assertEqual(summary["new_repositories_imported"], 211)
        self.assertEqual(summary["unique_repository_count_after"], 311)
        self.assertEqual(summary["transfer_duplicate_collapse_count"], 2)
        self.assertEqual(summary["unresolved_identity_count"], 0)
        self.assertEqual(summary["unresolved_identity_count_excluded"], 4)
        self.assertEqual(summary["supporting_reference_repository_count_excluded"], 19)
        self.assertEqual(summary["excluded_portfolio_repository_count"], 9)
        self.assertEqual(summary["unverified_or_nonpublic_repository_count_excluded"], 1)
        self.assertEqual(summary["license_unknown_count"], 100)
        self.assertEqual(summary["upstream_revision_unknown_count"], 0)
        self.assertEqual(summary["authority"], "descriptive-only")
        self.assertRegex(summary["transfer_upstream_revision"], r"^[0-9a-f]{40}$")
        self.assertNotIn("operated_repositories", self.data)
        for row in self.data["repositories"]:
            for source in row.get("portable_assessments", []):
                self.assertEqual(source["authority"], "evidence-only")
                self.assertTrue(source["source_links"])
                self.assertTrue(source["repository_stable_id"])
                self.assertTrue(source["assessment_artifact_ids"])
                self.assertTrue(source["source_content_sha256"])
                self.assertEqual(source["verification_method"], "github-rest-repository-and-default-branch-head")
                self.assertNotIn("source_path", source)

    def test_unresolved_identities_are_excluded_from_public_ledger(self):
        rows = self.data["unresolved_identities"]
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
