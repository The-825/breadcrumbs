import json
import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("workflow_registry", ROOT / "scripts/workflow_registry.py")
registry_tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(registry_tool)


class TestWorkflowRegistry(unittest.TestCase):
    def test_registry_is_public_descriptive_and_machine_routable(self):
        registry = json.loads((ROOT / "docs" / "workflow-registry.json").read_text(encoding="utf-8"))
        routing = json.loads((ROOT / "docs" / "jarvis-workflow-routing.json").read_text(encoding="utf-8"))
        workflow_ids = {row["id"] for row in registry["workflows"]}
        route_ids = {row["id"] for row in routing["routes"]}
        self.assertEqual("descriptive-only", registry["authority"])
        self.assertEqual("descriptive-only", routing["authority"])
        self.assertEqual([], registry_tool.validate(registry, routing))
        self.assertTrue(all(row["authority"] == "descriptive-only" for row in registry["workflows"]))
        self.assertTrue(all(set(row["jarvis_routes"]) <= route_ids for row in registry["workflows"]))
        self.assertTrue(all(set(row["workflow_ids"]) <= workflow_ids for row in routing["routes"]))

    def test_reproduced_is_not_adopted_or_claimed_effective(self):
        registry = json.loads((ROOT / "docs" / "workflow-registry.json").read_text(encoding="utf-8"))
        for row in registry["workflows"]:
            with self.subTest(workflow=row["id"]):
                if row["adoption_state"] == "reproduced":
                    self.assertEqual("public-synthetic-reproduction", row["evidence_level"])
                    self.assertEqual("passed", row["reproduction"]["result"])
                    self.assertIn("not external effectiveness", row["reproduction"]["claim_boundary"])
                elif row["adoption_state"] in {"discovered", "screened"}:
                    self.assertNotEqual("public-synthetic-reproduction", row["evidence_level"])

    def test_screened_primary_intake_does_not_need_a_fabricated_reproduction(self):
        registry = json.loads((ROOT / "docs/workflow-registry.json").read_text(encoding="utf-8"))
        routing = json.loads((ROOT / "docs/jarvis-workflow-routing.json").read_text(encoding="utf-8"))
        registry["schema_version"] = "1.1"
        candidate = copy.deepcopy(registry["workflows"][0])
        candidate.update(id="SYNTHETIC-WORKFLOW", source_type="official-documentation",
                         source_url="https://example.org/workflow", adoption_state="screened",
                         evidence_level="pinned-primary-documentation-screen")
        candidate.pop("reproduction", None)
        candidate["source_pin"] = dict(canonical_url=candidate["source_url"], version="synthetic revision",
                                       retrieved_date="2026-10-13", content_sha256="a" * 64, license_status="unknown")
        registry["workflows"].append(candidate)
        self.assertEqual([], registry_tool.validate(registry, routing))
        candidate["source_pin"].pop("content_sha256")
        self.assertTrue(registry_tool.validate(registry, routing))
        candidate["source_pin"]["content_sha256"] = "a" * 64
        candidate["adoption_state"] = "reproduced"
        self.assertTrue(registry_tool.validate(registry, routing))


if __name__ == "__main__":
    unittest.main()
