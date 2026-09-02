import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class TestWorkflowRegistry(unittest.TestCase):
    def test_registry_is_public_descriptive_and_machine_routable(self):
        registry = json.loads((ROOT / "docs" / "workflow-registry.json").read_text(encoding="utf-8"))
        routing = json.loads((ROOT / "docs" / "jarvis-workflow-routing.json").read_text(encoding="utf-8"))
        workflow_ids = {row["id"] for row in registry["workflows"]}
        route_ids = {row["id"] for row in routing["routes"]}
        self.assertEqual("descriptive-only", registry["authority"])
        self.assertEqual("descriptive-only", routing["authority"])
        self.assertTrue(all(row["source_url"].startswith("https://www.reddit.com/") for row in registry["workflows"]))
        self.assertTrue(all(set(row["jarvis_routes"]) <= route_ids for row in registry["workflows"]))
        self.assertTrue(all(set(row["workflow_ids"]) <= workflow_ids for row in routing["routes"]))

    def test_screened_is_not_reproduced_or_adopted(self):
        registry = json.loads((ROOT / "docs" / "workflow-registry.json").read_text(encoding="utf-8"))
        self.assertEqual({"screened"}, {row["adoption_state"] for row in registry["workflows"]})
        self.assertTrue(all(row["evidence_level"] == "screened-description" for row in registry["workflows"]))


if __name__ == "__main__":
    unittest.main()
