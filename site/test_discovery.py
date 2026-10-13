import copy
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import build_discovery as discovery


def inputs(count=125):
    priorities = dict(named_question="Synthetic recovery question", research=[], repositories=[])
    landscape = dict(repositories=[], popularity_observed_date="2026-10-01")
    for index in range(count):
        identity = f"TEST-{index:03}"
        common = dict(id=identity, url=f"https://example.org/{identity}", claims=["CI-006"], family="SYNTHETIC",
                      appraisal_priority_rank=1, priority_key=[0, 1, 3], priority_claim="CI-006")
        priorities["research"].append(dict(common, title=identity, review_depth="abstract-only", record_state="candidate-not-promoted", directness="D2 adjacent", horizon="technical"))
        priorities["repositories"].append(dict(common, repository=identity, review_depth="readme-screened"))
        landscape["repositories"].append(dict(id=identity, snapshot_commit="a" * 40, snapshot_date="2026-10-01",
                                              category="workflow-runtime", license_status="MIT", stars_observed=0))
    return priorities, landscape


class DiscoveryTests(unittest.TestCase):
    def test_first_edition_has_100_positions_without_invented_history(self):
        priorities, landscape = inputs()
        edition = discovery.make_edition("2026-10-12", priorities, landscape, [])
        for chart in edition["charts"].values():
            self.assertEqual(list(range(1, 101)), [row["position"] for row in chart["entries"]])
            self.assertEqual(125, chart["archive_count"])
            self.assertEqual(25, chart["cutoff_tied_outside_chart"])
            self.assertEqual(25, len(chart["off_chart_ids"]))
            self.assertTrue(all(row["movement"] is None and row["previous_position"] is None for row in chart["entries"]))
            self.assertTrue(all(row["entry_state"] == "new" and row["appearances"] == 1 for row in chart["entries"]))
        self.assertTrue(all(row["record_state"] == "candidate-not-promoted" for row in edition["charts"]["research"]["entries"]))

    def test_movement_peak_and_reentry_use_actual_editions(self):
        priorities, landscape = inputs(101)
        first = discovery.make_edition("2026-10-12", priorities, landscape, [])
        for kind in ("research", "repositories"):
            priorities[kind][-1]["priority_key"] = [-1, 1, 3]
        second = discovery.make_edition("2026-10-19", priorities, landscape, [first])
        row = second["charts"]["research"]["entries"][1]
        self.assertEqual("TEST-000", row["id"])
        self.assertEqual(-1, row["movement"])
        self.assertEqual(1, row["peak_position"])
        self.assertEqual(2, row["appearances"])
        for kind in ("research", "repositories"):
            priorities[kind][-1]["priority_key"] = [5, 1, 3]
        third = discovery.make_edition("2026-10-26", priorities, landscape, [first, second])
        returned = next(row for row in third["charts"]["research"]["entries"] if row["id"] == "TEST-099")
        self.assertEqual("reentry", returned["entry_state"])
        self.assertIsNone(returned["movement"])
        self.assertEqual(2, returned["appearances"])

    def test_portable_identity_cannot_inherit_chart_eligibility(self):
        priorities, landscape = inputs(3)
        priorities["repositories"][0]["review_depth"] = "source-assessment"
        edition = discovery.make_edition("2026-10-12", priorities, landscape, [])
        chart = edition["charts"]["repositories"]
        self.assertEqual(3, chart["archive_count"])
        self.assertEqual(2, chart["eligible_count"])
        self.assertNotIn("TEST-000", {row["id"] for row in chart["entries"]})

    def test_frozen_editions_are_immutable(self):
        priorities, landscape = inputs(2)
        edition = discovery.make_edition("2026-10-12", priorities, landscape, [])
        with TemporaryDirectory() as directory:
            path = Path(directory) / "2026-10-12.json"
            discovery.freeze(path, edition)
            original = path.read_bytes()
            changed = copy.deepcopy(edition)
            changed["question"] = "Different question"
            with self.assertRaisesRegex(ValueError, "cannot be overwritten"):
                discovery.freeze(path, changed)
            self.assertEqual(original, path.read_bytes())
        with self.assertRaises(ValueError):
            discovery.make_edition("2026-10-12", priorities, landscape, [edition])

    def test_duplicate_or_incomplete_priority_inputs_fail(self):
        priorities, landscape = inputs(2)
        duplicate = copy.deepcopy(priorities)
        duplicate["research"].append(duplicate["research"][0])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            discovery.make_edition("2026-10-12", duplicate, landscape, [])
        priorities["repositories"].pop()
        with self.assertRaisesRegex(ValueError, "cover"):
            discovery.make_edition("2026-10-12", priorities, landscape, [])

    def test_articles_need_steps_limits_and_safe_source_links(self):
        registry = discovery.read(discovery.DOCS / "workflow-registry.json")
        self.assertTrue({"WF-001", "WF-002", "WF-003", "WF-004", "WF-005"}.issubset(
            {row["id"] for row in discovery.workflow_catalog(registry)}))
        missing = copy.deepcopy(registry)
        missing["workflows"][0]["guide"]["completion_check"] = ""
        with self.assertRaisesRegex(ValueError, "completion_check"):
            discovery.workflow_catalog(missing)
        unsafe = copy.deepcopy(registry)
        unsafe["workflows"][0]["guide"]["artifacts"][0]["url"] = "javascript:alert(1)"
        with self.assertRaises(ValueError):
            discovery.workflow_catalog(unsafe)
        elevated = copy.deepcopy(registry)
        elevated["workflows"][0]["authority"] = "execute"
        with self.assertRaisesRegex(ValueError, "authority"):
            discovery.workflow_catalog(elevated)

    def test_stale_source_hashes_fail_before_an_edition_is_written(self):
        with TemporaryDirectory() as directory:
            docs = Path(directory)
            priorities, landscape = inputs(2)
            for name in ("collaborative-intelligence-research-ledger.md", "collaborative-intelligence-source-appraisals.md", "collaborative-intelligence-repository-landscape.json"):
                (docs / name).write_text(json.dumps(landscape), encoding="utf-8")
            priorities.update(research_source_sha256="0" * 64, appraisal_source_sha256="0" * 64, repository_source_sha256="0" * 64)
            (docs / "staletoast-appraisal-priorities.json").write_text(json.dumps(priorities), encoding="utf-8")
            history = docs / "history"
            with patch.object(discovery, "DOCS", docs), patch.object(discovery, "HISTORY", history), patch("sys.argv", ["build_discovery.py", "--edition-date", "2026-10-12"]):
                with self.assertRaisesRegex(ValueError, "stale"):
                    discovery.main()
            self.assertFalse(history.exists())

    def test_frozen_source_counts_match_the_current_first_edition(self):
        latest = next(row for row in discovery.editions() if row["edition_date"] == "2026-10-12")
        self.assertEqual(122, latest["charts"]["research"]["archive_count"])
        self.assertEqual(334, latest["charts"]["repositories"]["archive_count"])
        self.assertEqual(229, latest["charts"]["repositories"]["eligible_count"])
        self.assertEqual(100, len(latest["charts"]["research"]["entries"]))
        self.assertEqual(100, len(latest["charts"]["repositories"]["entries"]))


if __name__ == "__main__":
    unittest.main()
