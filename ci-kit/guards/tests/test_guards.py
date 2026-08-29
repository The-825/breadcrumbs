"""Guard self-tests: every guard bites a bad fixture.

For each of the six CI lint guards, run it (as a subprocess, the same way CI
does) against a deliberately-bad fixture and assert a non-zero exit, then
against a clean fixture and assert exit 0. This is the proof the guards
actually block. A guard that never fails is worse than no guard, so "every
guard bites its bad fixture" belongs on your Phase 0 exit criteria.
"""
import os
import subprocess
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_GUARDS_DIR = os.path.dirname(_HERE)                      # ci-kit/guards
_REPO = os.path.dirname(os.path.dirname(_GUARDS_DIR))     # repo root
_BAD = os.path.join(_HERE, "bad_fixtures")
_GOOD = os.path.join(_HERE, "good_fixtures")

# guard filename -> (bad fixture, good fixture)
CASES = {
    "guard_no_inline_style_script.py": ("bad_inline.html", "good_inline.html"),
    "guard_env_var_in_config.py": ("bad_env.py", "good_env.py"),
    "guard_no_raw_fetch.py": ("bad_fetch.js", "good_fetch.js"),
    "guard_no_magic_limit.py": ("bad_limit.sql", "good_limit.sql"),
    "guard_no_raw_create_view.py": ("bad_create_view.sql", "good_select.sql"),
    "guard_no_pii_in_fixtures.py": ("bad_pii_fixture.json", "good_pii_fixture.json"),
}


def _run(guard, target):
    return subprocess.run(
        [sys.executable, os.path.join(_GUARDS_DIR, guard), target],
        cwd=_REPO, capture_output=True, text=True,
    )


class TestGuardsBite(unittest.TestCase):
    def test_each_guard_fails_bad_fixture(self):
        for guard, (bad, _good) in CASES.items():
            with self.subTest(guard=guard):
                res = _run(guard, os.path.join(_BAD, bad))
                self.assertNotEqual(
                    res.returncode, 0,
                    f"{guard} did NOT fail its bad fixture {bad}\n{res.stdout}\n{res.stderr}",
                )

    def test_each_guard_passes_good_fixture(self):
        for guard, (_bad, good) in CASES.items():
            with self.subTest(guard=guard):
                res = _run(guard, os.path.join(_GOOD, good))
                self.assertEqual(
                    res.returncode, 0,
                    f"{guard} false-positived on clean fixture {good}\n{res.stdout}\n{res.stderr}",
                )

    def test_pii_guard_stdin_mode_bites_and_passes(self):
        # The same detector, fed over stdin instead of a file path: this is
        # the mode the outbound-payload hook and a pre-push git guard share.
        # See templates/hooks/outbound-pii-screen.md.
        guard = os.path.join(_GUARDS_DIR, "guard_no_pii_in_fixtures.py")
        with open(os.path.join(_BAD, "bad_pii_fixture.json"), encoding="utf-8") as f:
            bad_res = subprocess.run(
                [sys.executable, guard, "--stdin"],
                input=f.read(), cwd=_REPO, capture_output=True, text=True,
            )
        self.assertNotEqual(bad_res.returncode, 0, bad_res.stdout + bad_res.stderr)

        with open(os.path.join(_GOOD, "good_pii_fixture.json"), encoding="utf-8") as f:
            good_res = subprocess.run(
                [sys.executable, guard, "--stdin"],
                input=f.read(), cwd=_REPO, capture_output=True, text=True,
            )
        self.assertEqual(good_res.returncode, 0, good_res.stdout + good_res.stderr)

    def test_pii_guard_allows_digits_inside_a_public_repository_handle(self):
        guard = os.path.join(_GUARDS_DIR, "guard_no_pii_in_fixtures.py")
        res = subprocess.run(
            [sys.executable, guard, "--stdin"],
            input='{"repository":"Mark393295827/public-tool"}',
            cwd=_REPO,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)


if __name__ == "__main__":
    unittest.main()
