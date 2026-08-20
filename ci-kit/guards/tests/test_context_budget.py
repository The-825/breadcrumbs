"""Self-tests for guard_context_budget.py: the guard bites its bad fixtures.

Runs the guard as a subprocess, the same way CI does, against a manifest whose
budgeted file is over its line budget (must fail), one whose file is under
(must pass), and this repo's real CONTEXT_BUDGET.md (must pass, so a boot-set
file that grew past its budget fails here as well as in run_guards.sh). Also
proves the guard's own --selftest fixture suite is green, and that --report
never fails the build even when a file is over budget, since the ratchet pass
is meant to be safe to run anywhere.
"""
import os
import subprocess
import sys
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_GUARDS_DIR = os.path.dirname(_HERE)                      # ci-kit/guards
_REPO = os.path.dirname(os.path.dirname(_GUARDS_DIR))     # repo root
_GUARD = os.path.join(_GUARDS_DIR, "guard_context_budget.py")
_REAL_MANIFEST = os.path.join(_REPO, "CONTEXT_BUDGET.md")

TABLE = (
    "| File | Class | budget_lines | Notes |\n"
    "|---|---|---:|---|\n"
    "| `boot.md` | kernel | 5 | binding rules only |\n"
)


def _run(args):
    return subprocess.run(
        [sys.executable, _GUARD] + args,
        capture_output=True, text=True,
    )


def _tree(nlines):
    """Build a temp repo with a manifest and a boot.md of nlines lines."""
    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "manifest.md"), "w", encoding="utf-8") as fh:
        fh.write(TABLE)
    with open(os.path.join(tmp, "boot.md"), "w", encoding="utf-8") as fh:
        fh.write("".join("x\n" for _ in range(nlines)))
    return tmp


class TestContextBudgetGuard(unittest.TestCase):
    def test_over_budget_fails(self):
        tmp = _tree(9)
        res = _run(["--manifest", os.path.join(tmp, "manifest.md"), "--root", tmp])
        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        self.assertIn("over by 4", res.stdout)

    def test_under_budget_passes(self):
        tmp = _tree(3)
        res = _run(["--manifest", os.path.join(tmp, "manifest.md"), "--root", tmp])
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)

    def test_report_never_fails(self):
        tmp = _tree(9)
        res = _run(["--manifest", os.path.join(tmp, "manifest.md"), "--root", tmp,
                    "--report"])
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("headroom", res.stdout)

    def test_missing_manifest_fails_closed(self):
        res = _run(["--manifest", os.path.join(_HERE, "no_such_manifest.md")])
        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)

    def test_this_repo_is_inside_its_own_budget(self):
        self.assertTrue(os.path.isfile(_REAL_MANIFEST), "CONTEXT_BUDGET.md missing")
        res = _run(["--manifest", _REAL_MANIFEST, "--root", _REPO])
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)

    def test_guard_selftest_passes(self):
        res = _run(["--selftest"])
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)


if __name__ == "__main__":
    unittest.main()
