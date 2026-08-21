import copy
import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "breadcrumb_score.py"
SPEC = importlib.util.spec_from_file_location("breadcrumb_score", MODULE_PATH)
breadcrumb_score = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(breadcrumb_score)
AssessmentError = breadcrumb_score.AssessmentError
DIMENSIONS = breadcrumb_score.DIMENSIONS
score = breadcrumb_score.score


def fixture(scored=5):
    dimensions = {}
    for index, name in enumerate(DIMENSIONS):
        if index < scored:
            dimensions[name] = {
                "score": 4,
                "evidence_class": "tested",
                "evidence": [{
                    "claim": f"{name} is exercised",
                    "source": f"tests/{name}.py",
                    "observed_at": "2026-08-21",
                }],
            }
        else:
            dimensions[name] = {"score": None, "evidence_class": None, "evidence": []}
    return {
        "schema_version": "0.1.0",
        "status": "draft",
        "target": {
            "name": "example/repository",
            "owner": "example",
            "purpose": "Demonstrate scoring",
            "evidence_scope": "Public repository at a named revision",
        },
        "owner_opt_in": True,
        "human_reviewed": False,
        "assessed_at": "2026-08-21",
        "publication_approval": None,
        "supersedes": None,
        "withdrawal_reason": None,
        "dimensions": dimensions,
    }


class BreadcrumbScoreTests(unittest.TestCase):
    def test_unknown_dimensions_reduce_coverage_without_becoming_zeroes(self):
        result = score(fixture(scored=5))
        self.assertEqual(result["tested_dimensions"], 5)
        self.assertEqual(result["evidence_coverage"], 0.625)
        self.assertEqual(len(result["dimension_scores"]), 5)
        self.assertEqual(result["weighted_score"], 4.0)

    def test_fewer_than_five_scored_dimensions_withholds_readiness(self):
        result = score(fixture(scored=4))
        self.assertIsNone(result["weighted_score"])
        self.assertEqual(result["readiness_band"], "insufficient_evidence")

    def test_scored_dimension_requires_cited_evidence(self):
        assessment = fixture()
        assessment["dimensions"][DIMENSIONS[0]]["evidence"] = []
        with self.assertRaisesRegex(AssessmentError, "requires evidence"):
            score(assessment)

    def test_public_ready_status_requires_human_review(self):
        assessment = fixture()
        assessment["status"] = "owner_reviewed"
        with self.assertRaisesRegex(AssessmentError, "human_reviewed"):
            score(assessment)

    def test_published_status_requires_specific_approval_record(self):
        assessment = fixture()
        assessment["status"] = "published"
        assessment["human_reviewed"] = True
        with self.assertRaisesRegex(AssessmentError, "publication_approval"):
            score(assessment)

    def test_owner_opt_in_is_mandatory(self):
        assessment = fixture()
        assessment["owner_opt_in"] = False
        with self.assertRaisesRegex(AssessmentError, "owner_opt_in"):
            score(assessment)

    def test_superseded_assessment_links_to_the_prior_digest(self):
        assessment = fixture()
        assessment["status"] = "superseded"
        with self.assertRaisesRegex(AssessmentError, "supersedes"):
            score(assessment)
        assessment["supersedes"] = "sha256:prior-assessment"
        self.assertEqual(score(assessment)["status"], "superseded")

    def test_withdrawal_preserves_a_reason(self):
        assessment = fixture()
        assessment["status"] = "withdrawn"
        with self.assertRaisesRegex(AssessmentError, "withdrawal_reason"):
            score(assessment)
        assessment["withdrawal_reason"] = "Owner withdrew the card from discovery"
        self.assertEqual(score(assessment)["status"], "withdrawn")

    def test_digest_is_deterministic(self):
        assessment = fixture(scored=8)
        first = score(assessment)
        second = score(copy.deepcopy(assessment))
        self.assertEqual(first, second)

    def test_unknown_dimension_name_fails_closed(self):
        assessment = fixture()
        assessment["dimensions"]["marketing_claim"] = {
            "score": 5,
            "evidence_class": "declared",
            "evidence": [],
        }
        with self.assertRaisesRegex(AssessmentError, "unknown dimensions"):
            score(assessment)


if __name__ == "__main__":
    unittest.main()
