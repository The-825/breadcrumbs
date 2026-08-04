"""Self-tests for guard_authority_citations.py: the guard bites its bad fixtures.

Runs the guard as a subprocess, the same way CI does, against a deliberately
broken ledger fixture (must fail), a clean ledger fixture (must pass), and
synthetic GitHub event payloads exercising the citation paths (valid passes;
unknown and revoked citations fail). Also proves the shipped starter ledger
passes the guard (via a fixture copy in good_fixtures/, so the suite stays
green in an adopter tree that copied only ci-kit/), that the companion repo's
templates/authority_ledger.jsonl has not drifted from that fixture (skipped
when the templates tree is absent), and that the guard's own --selftest
fixture suite is green.

GITHUB_EVENT_PATH is controlled explicitly per case: popped for the no-event
cases (CI always sets it, so inheriting the real one would leak the host
event into the test) and pointed at a temp payload for the citation cases.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_GUARDS_DIR = os.path.dirname(_HERE)                      # ci-kit/guards
_REPO = os.path.dirname(os.path.dirname(_GUARDS_DIR))     # repo root
_GUARD = os.path.join(_GUARDS_DIR, "guard_authority_citations.py")
_BAD_LEDGER = os.path.join(_HERE, "bad_fixtures", "bad_authority_ledger.jsonl")
_GOOD_LEDGER = os.path.join(_HERE, "good_fixtures", "good_authority_ledger.jsonl")
_STARTER_FIXTURE = os.path.join(_HERE, "good_fixtures", "starter_ledger.jsonl")
_REPO_STARTER = os.path.join(_REPO, "templates", "authority_ledger.jsonl")

# Ids in the good fixture: G-20260101-01 is active, G-20260102-01 is revoked.
ACTIVE_ID = "G-20260101-01"
REVOKED_ID = "G-20260102-01"


def _run(args, event_body=None):
    """Run the guard with a controlled environment.

    event_body None -> GITHUB_EVENT_PATH removed (no-event case).
    event_body str  -> a temp pull_request event payload carrying that body.
    """
    env = os.environ.copy()
    env.pop("GITHUB_EVENT_PATH", None)
    env.pop("AUTHORITY_LEDGER_PATH", None)
    tmp = None
    try:
        if event_body is not None:
            tmp = tempfile.NamedTemporaryFile(
                "w", suffix=".json", delete=False, encoding="utf-8"
            )
            json.dump({"pull_request": {"body": event_body}}, tmp)
            tmp.close()
            env["GITHUB_EVENT_PATH"] = tmp.name
        return subprocess.run(
            [sys.executable, _GUARD] + args,
            cwd=_REPO, capture_output=True, text=True, env=env,
        )
    finally:
        if tmp is not None:
            os.unlink(tmp.name)


class TestAuthorityCitationsGuard(unittest.TestCase):
    def test_selftest_passes(self):
        res = _run(["--selftest"])
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("SELFTEST OK", res.stdout)

    def test_bad_ledger_fixture_bites(self):
        res = _run(["--ledger", _BAD_LEDGER])
        self.assertNotEqual(
            res.returncode, 0,
            f"guard did NOT fail the bad ledger fixture\n{res.stdout}\n{res.stderr}",
        )
        self.assertIn("ledger integrity", res.stdout)

    def test_good_ledger_passes_without_event(self):
        res = _run(["--ledger", _GOOD_LEDGER])
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)

    def test_valid_citation_passes(self):
        res = _run(["--ledger", _GOOD_LEDGER],
                   event_body=f"Summary\n\nAuthority: {ACTIVE_ID}\n")
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn(ACTIVE_ID, res.stdout)

    def test_unknown_citation_bites(self):
        res = _run(["--ledger", _GOOD_LEDGER],
                   event_body="Authority: G-19990101-99")
        self.assertNotEqual(
            res.returncode, 0,
            f"guard did NOT fail an unknown citation\n{res.stdout}\n{res.stderr}",
        )

    def test_revoked_citation_bites(self):
        res = _run(["--ledger", _GOOD_LEDGER],
                   event_body=f"Authority: {REVOKED_ID}")
        self.assertNotEqual(
            res.returncode, 0,
            f"guard did NOT fail a revoked citation\n{res.stdout}\n{res.stderr}",
        )

    def test_shipped_starter_ledger_passes(self):
        res = _run(["--ledger", _STARTER_FIXTURE])
        self.assertEqual(
            res.returncode, 0,
            f"shipped starter ledger failed its own guard\n{res.stdout}\n{res.stderr}",
        )

    @unittest.skipUnless(
        os.path.exists(_REPO_STARTER),
        "templates/authority_ledger.jsonl not present in this tree (kit-only copy)",
    )
    def test_repo_starter_matches_fixture(self):
        with open(_REPO_STARTER, encoding="utf-8") as f:
            repo_copy = f.read()
        with open(_STARTER_FIXTURE, encoding="utf-8") as f:
            fixture = f.read()
        self.assertEqual(
            repo_copy, fixture,
            "templates/authority_ledger.jsonl drifted from "
            "good_fixtures/starter_ledger.jsonl; update the fixture copy to match",
        )


if __name__ == "__main__":
    unittest.main()
