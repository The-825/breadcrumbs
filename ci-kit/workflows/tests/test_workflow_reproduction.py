"""Synthetic tests for reproduction evidence dates, with no real subprocesses."""

import contextlib
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock


SOURCE = Path(__file__).resolve().parents[3] / "scripts" / "workflow_reproduction.py"
SPEC = importlib.util.spec_from_file_location("workflow_reproduction", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReproductionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.registry = Path(self.temp.name) / "registry.json"
        self.routing = Path(self.temp.name) / "routing.json"
        self.now = datetime(2026, 10, 13, 23, 59, 59, tzinfo=timezone.utc)
        self.clock = Mock(side_effect=lambda: self.now)
        self.runner = Mock(return_value=Mock(returncode=0))
        self.data = {"workflows": [
            {"id": key, "jarvis_routes": ["route"]} for key in MODULE.COMMANDS
        ]}
        self.routing.write_text(json.dumps({"routes": [{"id": "route"}]}), encoding="utf-8")
        self.save()

    def save(self):
        self.registry.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def invoke(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = MODULE.main(list(args), registry_path=self.registry, routing_path=self.routing,
                               runner=self.runner, clock=self.clock)
        return code, output.getvalue()

    def load(self):
        self.data = json.loads(self.registry.read_text(encoding="utf-8"))
        return self.data

    def seed(self):
        self.assertEqual(self.invoke("--write")[0], 0)
        self.load()
        self.runner.reset_mock()
        self.clock.reset_mock()

    def test_write_records_actual_utc_date_once_and_runner_contract(self):
        self.now = datetime(2026, 10, 13, 20, tzinfo=timezone(timedelta(hours=-7)))
        self.assertEqual(self.invoke("--write")[0], 0)
        for row in self.load()["workflows"]:
            self.assertEqual(row["reproduction"]["date"], "2026-10-14")
            self.assertEqual(row["reproduction"]["command"], " ".join(MODULE.COMMANDS[row["id"]][1:]))
        self.clock.assert_called_once_with()
        self.assertEqual(self.runner.call_count, len(MODULE.COMMANDS))
        for call in self.runner.call_args_list:
            self.assertEqual(call.kwargs, {"cwd": MODULE.ROOT, "text": True, "capture_output": True})
        self.assertNotIn(b"\r\n", self.registry.read_bytes())

    def test_later_day_check_preserves_history_and_write_refreshes(self):
        self.seed()
        before = self.registry.read_bytes()
        self.now += timedelta(days=8)
        self.assertEqual(self.invoke("--check")[0], 0)
        self.assertEqual(self.registry.read_bytes(), before)
        self.assertEqual(self.invoke("--write")[0], 0)
        self.assertEqual(self.load()["workflows"][0]["reproduction"]["date"], "2026-10-21")

    def test_invalid_dates_fail_check_and_run_commands(self):
        self.seed()
        invalid = [None, 42, "", "20261013", "2026-W42-2", "2026-02-30",
                   "2026-10-13T00:00:00Z", "2026-10-14"]
        for value in invalid:
            with self.subTest(value=value):
                self.data["workflows"][0]["reproduction"]["date"] = value
                self.save()
                before = self.registry.read_bytes()
                self.runner.reset_mock()
                code, output = self.invoke("--check")
                self.assertEqual(code, 1)
                self.assertIn("WF-001:", output)
                self.assertEqual(self.runner.call_count, len(MODULE.COMMANDS))
                self.assertEqual(self.registry.read_bytes(), before)
        del self.data["workflows"][0]["reproduction"]["date"]
        self.save()
        self.assertEqual(self.invoke("--check")[0], 1)
        self.data["workflows"][0]["reproduction"] = []
        self.save()
        self.assertEqual(self.invoke("--check")[0], 1)

    def test_future_date_becomes_valid_at_utc_boundary(self):
        self.seed()
        self.data["workflows"][0]["reproduction"]["date"] = "2026-10-14"
        self.save()
        self.assertEqual(self.invoke("--check")[0], 1)
        self.now += timedelta(seconds=1)
        self.assertEqual(self.invoke("--check")[0], 0)

    def test_naive_clock_rejected_before_commands_or_write(self):
        before = self.registry.read_bytes()
        self.now = datetime(2026, 10, 13)
        with self.assertRaisesRegex(ValueError, "aware datetime"):
            self.invoke("--write")
        self.runner.assert_not_called()
        self.assertEqual(self.registry.read_bytes(), before)

    def test_all_metadata_drift_fails_with_valid_date(self):
        self.seed()
        baseline = json.loads(json.dumps(self.data))
        for field in ["adoption_state", "evidence_level", "command", "result", "claim_boundary"]:
            with self.subTest(field=field):
                self.data = json.loads(json.dumps(baseline))
                target = self.data["workflows"][0]
                if field not in ["adoption_state", "evidence_level"]:
                    target = target["reproduction"]
                target[field] = "drift"
                self.save()
                self.assertEqual(self.invoke("--check")[0], 1)

    def test_missing_records_and_routes_skip_only_their_runners(self):
        self.data["workflows"].pop(0)
        self.data["workflows"][0]["jarvis_routes"] = ["missing"]
        self.save()
        before = self.registry.read_bytes()
        code, output = self.invoke("--write")
        self.assertEqual(code, 1)
        self.assertIn("WF-001: registry record is missing", output)
        self.assertIn("WF-002: routable completion contract is missing", output)
        self.assertEqual(self.runner.call_count, len(MODULE.COMMANDS) - 2)
        self.assertEqual(self.registry.read_bytes(), before)
        self.assertEqual([call.args[0] for call in self.runner.call_args_list], list(MODULE.COMMANDS.values())[2:])

    def test_failed_write_and_plain_runs_preserve_bytes_and_collect_errors(self):
        before = self.registry.read_bytes()
        self.runner.return_value = Mock(returncode=1)
        for args in [("--write",), ()]:
            code, output = self.invoke(*args)
            self.assertEqual(code, 1)
            self.assertEqual(output.count("reproduction command failed"), len(MODULE.COMMANDS))
            self.assertEqual(self.registry.read_bytes(), before)
        self.runner.return_value = Mock(returncode=0)
        self.assertEqual(self.invoke()[0], 0)
        self.assertEqual(self.registry.read_bytes(), before)
        self.runner.side_effect = [Mock(returncode=int(index == 2)) for index in range(len(MODULE.COMMANDS))]
        self.assertEqual(self.invoke("--write")[0], 1)
        self.assertEqual(self.registry.read_bytes(), before)

    def test_flags_exclusive_before_clock_or_runner(self):
        before = self.registry.read_bytes()
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            self.invoke("--write", "--check")
        self.assertEqual(caught.exception.code, 2)
        self.runner.assert_not_called()
        self.clock.assert_not_called()
        self.assertEqual(self.registry.read_bytes(), before)

    def test_unrelated_nested_nonascii_record_preserved_and_summary_truthful(self):
        unrelated = {"id": "WF-099", "nested": {"label": "caf\u00e9", "rows": [1, {"value": "\u96ea"}]}}
        self.data["workflows"].append(unrelated)
        self.save()
        code, output = self.invoke("--write")
        self.assertEqual(code, 0)
        self.assertEqual(self.load()["workflows"][-1], unrelated)
        self.assertIn(f"reproduced={len(MODULE.COMMANDS)} adopted=0 effectiveness_claims=0", output)
        original = MODULE.COMMANDS
        try:
            MODULE.COMMANDS = dict(list(original.items())[:2])
            self.assertIn("reproduced=2 adopted=0 effectiveness_claims=0", self.invoke()[1])
        finally:
            MODULE.COMMANDS = original


if __name__ == "__main__":
    unittest.main()
