import importlib.util
import json
import os
import unittest


_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _load(name, relative_path):
    path = os.path.join(_REPO, relative_path)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PortfolioContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(_REPO, "kit.json"), encoding="utf-8") as handle:
            cls.manifest = json.load(handle)
        with open(
            os.path.join(
                _REPO,
                "docs",
                "collaborative-intelligence-repository-landscape.json",
            ),
            encoding="utf-8",
        ) as handle:
            cls.ledger = json.load(handle)
        cls.importer = _load("repository_landscape", "scripts/repository_landscape.py")
        cls.checker = _load("kit_manifest_check", "ci-kit/kit_manifest_check.py")

    def test_consumer_discovers_breadcrumbs_as_owner_from_machine_data(self):
        contract = self.manifest["portfolio_contract"]
        capability = "portable-repository-identity-and-provenance-intake"
        self.assertIn(capability, contract["owns"])
        self.assertEqual(contract["canonical_owner"], "The-825/breadcrumbs")
        self.assertEqual(
            contract["role"], "reusable-public-pattern-and-assessment-owner"
        )

    def test_contract_matches_importer_and_source_keeps_authority(self):
        self.assertEqual(
            self.checker.check_portfolio_contract(self.manifest, self.checker.ROOT), []
        )
        contract = self.manifest["portfolio_contract"]
        self.assertIn("operational-authority", contract["source_retains"])
        self.assertEqual(contract["transfer_contract"]["authority"], "evidence-only")
        self.assertTrue(contract["transfer_contract"]["fail_closed"])

    def test_private_or_operated_transfer_rows_fail_closed(self):
        row = self._valid_row()
        for record_type in (
            "operated_repository",
            "private_repository",
            "source_context_repository",
        ):
            with self.subTest(record_type=record_type):
                candidate = dict(row, record_type=record_type)
                with self.assertRaisesRegex(ValueError, "non-external-public"):
                    self.importer.validate_transfer_record(candidate)

    def test_public_visibility_and_nonauthorization_are_required(self):
        missing_visibility = self._valid_row()
        missing_visibility["public_source_links"] = []
        with self.assertRaisesRegex(ValueError, "visibility proof"):
            self.importer.validate_transfer_record(missing_visibility)

        authority_grant = self._valid_row()
        authority_grant["authority"] = "may install and act"
        with self.assertRaisesRegex(ValueError, "evidence-only"):
            self.importer.validate_transfer_record(authority_grant)

        private_payload = self._valid_row()
        private_payload["student_record"] = "not transferable"
        with self.assertRaisesRegex(ValueError, "prohibited fields"):
            self.importer.validate_transfer_record(private_payload)

    def test_portable_and_detailed_evidence_classes_remain_distinct(self):
        rows = self.ledger["repositories"]
        detailed = [row for row in rows if row["evidence_depth"] == "readme-screened"]
        portable = [row for row in rows if row["evidence_depth"] == "source-assessment"]
        evidence = self.manifest["portfolio_contract"]["evidence_classes"]
        self.assertGreaterEqual(
            len(detailed),
            evidence["detailed_appraisal"]["saturation_baseline_count"],
        )
        self.assertEqual(len(detailed), evidence["detailed_appraisal"]["current_count"])
        self.assertEqual(len(detailed), 206)
        self.assertEqual(len(portable), 105)
        self.assertTrue(evidence["portable_intake"]["may_expand"])
        self.assertFalse(
            evidence["portable_intake"]["claims_detailed_mechanism_review"]
        )

    @staticmethod
    def _valid_row():
        return {
            "record_type": "assessed_external_public_repository",
            "stable_id": "public-repository:test",
            "canonical_key": "public-owner/public-repository",
            "owner": "public-owner",
            "repo": "public-repository",
            "public_source_links": [
                "https://github.com/public-owner/public-repository"
            ],
            "source_artifact_ids": ["public-assessment:test"],
            "assessment_date": "2026-08-29",
            "license": "unknown",
            "upstream_revision": "a" * 40,
            "authority": "evidence-only",
            "source_content_sha256": ["b" * 64],
            "visibility": "public",
            "verification_source": "https://api.github.com/repos/public-owner/public-repository",
            "verification_method": "github-rest-repository-and-default-branch-head",
            "verification_date": "2026-08-29",
            "source_revision": "a" * 40,
            "license_status": "unknown",
            "public_github_url": "https://github.com/public-owner/public-repository",
            "aliases": [],
        }


if __name__ == "__main__":
    unittest.main()
