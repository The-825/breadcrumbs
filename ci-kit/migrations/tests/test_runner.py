"""Migration runner tests.

Proves the runner REJECTS a duplicate migration number and an out-of-order
migration, and ACCEPTS a clean forward-only sequence. Builds throwaway
migration folders and ledgers in temp dirs so nothing touches the real folder.
"The runner refuses both failure classes" belongs on your Phase 0 exit
criteria next to "every guard bites its bad fixture."
"""
import importlib.util
import json
import os
import tempfile
import unittest

_RUNNER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runner.py")


def _load_runner():
    spec = importlib.util.spec_from_file_location("runner", _RUNNER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


runner = _load_runner()


def _touch(d, name):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        f.write(f"-- {name}\n")


def _write_ledger(path, mapping):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mapping, f)


class TestDiscover(unittest.TestCase):
    def test_clean_sequence_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            _touch(d, "001_a.sql")
            _touch(d, "002_b.sql")
            _touch(d, "003_c.sql")
            found = runner.discover(d)
            self.assertEqual([n for n, _ in found], [1, 2, 3])

    def test_duplicate_number_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            _touch(d, "001_a.sql")
            _touch(d, "001_b.sql")   # duplicate NNN
            with self.assertRaises(runner.DuplicateNumberError):
                runner.discover(d)

    def test_validate_reports_duplicate(self):
        with tempfile.TemporaryDirectory() as d:
            _touch(d, "005_x.sql")
            _touch(d, "005_y.sql")
            problems = runner.validate(d)
            self.assertTrue(problems)


class TestApplyOrder(unittest.TestCase):
    def test_out_of_order_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            _touch(d, "001_a.sql")
            _touch(d, "002_b.sql")
            _touch(d, "003_c.sql")
            ledger_path = os.path.join(d, "ledger.json")
            # 003 already applied; 002 still pending => 002 is behind the frontier.
            _write_ledger(ledger_path, {"t1": ["001_a.sql", "003_c.sql"]})
            ledger = runner.load_ledger(ledger_path)
            with self.assertRaises(runner.OutOfOrderError):
                runner.check_apply_order(d, ledger, "t1")

    def test_forward_only_sequence_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            _touch(d, "001_a.sql")
            _touch(d, "002_b.sql")
            _touch(d, "003_c.sql")
            ledger_path = os.path.join(d, "ledger.json")
            _write_ledger(ledger_path, {"t1": ["001_a.sql"]})
            ledger = runner.load_ledger(ledger_path)
            # 002 and 003 are both above the frontier => no error.
            runner.check_apply_order(d, ledger, "t1")
            self.assertEqual(runner.pending(d, ledger, "t1"), ["002_b.sql", "003_c.sql"])


if __name__ == "__main__":
    unittest.main()
