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
        self.assertEqual(len(rows), 15)
        self.assertEqual(len({row["id"] for row in rows}), len(rows))
        self.assertEqual(len({row["repository"].lower() for row in rows}), len(rows))
        for row in rows:
            self.assertRegex(row["id"], r"^R-\d{3}$")
            self.assertRegex(row["snapshot_commit"], r"^[0-9a-f]{40}$")
            self.assertRegex(row["snapshot_date"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertEqual(row["url"], f"https://github.com/{row['repository']}")

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
            self.assertTrue(row["claims"])
            for claim in row["claims"]:
                match = re.fullmatch(r"CI-(\d{3})", claim)
                self.assertIsNotNone(match)
                self.assertIn(int(match.group(1)), range(1, 18))

    def test_current_wave_does_not_overstate_depth(self):
        for row in self.data["repositories"]:
            self.assertEqual(row["lifecycle"], "current")
            self.assertEqual(row["evidence_depth"], "readme-screened")
            self.assertEqual(row["evidence_pointer"], "README.md")


if __name__ == "__main__":
    unittest.main()
