"""Unit tests for decision_script.py (the second-generation merge gate).

The fail-closed floor is the contract: drafts never merge, zero check runs
never merge, a failing check or dirty/unknown mergeable state never merges,
an unlistable changed-file set never merges label-free, and a PR that edits
its own merge gate never self-merges. Every one of those sentences has a
test here; if you edit the script, these tests are what keeps the floor
from decaying quietly.

The script lives outside a package (it deploys to your workflow-scripts
directory), so it is loaded by file path. Run from the repo root:

    python3 -m unittest discover -s ci-kit/workflows/tests

Adopters: carry this file into your own test tree next to wherever you
deploy the script, and add the discovery line to your checks workflow so
the gate's own tests gate changes to the gate.
"""
import importlib.util
import io
import json
import os
import re
import tempfile
import unittest
from contextlib import redirect_stdout

_SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "decision_script.py")


def _load():
    spec = importlib.util.spec_from_file_location("decision_script", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ds = _load()

GREEN = [
    {"name": "Static checks", "status": "completed", "conclusion": "success"},
    {"name": "E2E checks", "status": "completed", "conclusion": "success"},
]


def lane(files, labels=(), head="agent/feature", base="main", draft=False,
         require_label=False, **kw):
    """Rung-two lane call by default; tests for rung one pass require_label=True."""
    return ds.lane_decision(base, head, list(labels), draft, files,
                            require_label=require_label, **kw)


class TestLaneScope(unittest.TestCase):
    """PRs the gate refuses to consider at all."""

    def test_draft_never_merges_on_either_rung(self):
        for rung in (True, False):
            verdict, reason = lane(["src/x.py"], draft=True, require_label=rung)
            self.assertEqual(verdict, "wait")
            self.assertIn("draft", reason)

    def test_draft_with_label_still_never_merges(self):
        verdict, _ = lane(["src/x.py"], labels=[ds.APPROVAL_LABEL], draft=True)
        self.assertEqual(verdict, "wait")

    def test_non_main_base_waits(self):
        verdict, _ = lane(["src/x.py"], base="release")
        self.assertEqual(verdict, "wait")

    def test_non_agent_head_waits(self):
        verdict, _ = lane(["src/x.py"], head="feature/manual-work")
        self.assertEqual(verdict, "wait")


class TestMaturityLadder(unittest.TestCase):
    """Rung one (label-gated) vs rung two (label-free with protected paths)."""

    def test_shipped_default_is_rung_one(self):
        # The kit ships REQUIRE_LABEL = True: a green unlabeled agent PR
        # waits. Graduating to label-free is a deliberate operator edit.
        self.assertTrue(ds.REQUIRE_LABEL)
        verdict, reason = ds.lane_decision("main", "agent/x", [], False, ["src/x.py"])
        self.assertEqual(verdict, "wait")
        self.assertIn("rung one", reason)

    def test_rung_one_label_releases_the_merge(self):
        verdict, reason = lane(["src/x.py"], labels=[ds.APPROVAL_LABEL],
                               require_label=True)
        self.assertEqual(verdict, "merge")
        self.assertIn("release", reason)

    def test_rung_two_clean_pr_merges_label_free(self):
        verdict, reason = lane(["src/x.py", "docs-src/y.txt"])
        self.assertEqual(verdict, "merge")
        self.assertIn("label-free", reason)


class TestProtectedPaths(unittest.TestCase):
    """The machinery keeps the human gate on the label-free rung."""

    def test_a_pr_that_edits_its_own_merge_gate_never_self_merges(self):
        # The core principle. Both default protected entries are the gate's
        # own moving parts.
        for path in [".github/workflows/automerge.yml",
                     ".github/scripts/decision_script.py"]:
            verdict, reason = lane([path, "src/unrelated.py"])
            self.assertEqual(verdict, "wait", path)
            self.assertIn("protected paths", reason)

    def test_label_overrides_protected_paths(self):
        verdict, _ = lane([".github/scripts/decision_script.py"],
                          labels=[ds.APPROVAL_LABEL])
        self.assertEqual(verdict, "merge")

    def test_trailing_slash_protects_the_whole_tree(self):
        protected = ["infra-templates/"]
        verdict, _ = lane(["infra-templates/network/core.tf"], protected=protected)
        self.assertEqual(verdict, "wait")

    def test_exact_entry_does_not_match_a_lookalike(self):
        verdict, _ = lane([".github/workflows/automerge.yml.bak"])
        self.assertEqual(verdict, "merge")

    def test_unlistable_files_fail_closed(self):
        verdict, reason = lane(None)
        self.assertEqual(verdict, "wait")
        self.assertIn("failing closed", reason)

    def test_label_overrides_unlistable_files(self):
        # The label is the human's explicit release; the human looked.
        verdict, _ = lane(None, labels=[ds.APPROVAL_LABEL])
        self.assertEqual(verdict, "merge")


class TestContentPolicies(unittest.TestCase):
    """A path family off the protected list is gated by its content lint."""

    def test_violations_reattach_the_label_requirement(self):
        policies = (("migrations/", lambda scoped, h, b: ["bad statement"]),)
        verdict, reason = lane(["migrations/011_x.sql"],
                               head_root=".", base_root=".",
                               content_policies=policies)
        self.assertEqual(verdict, "wait")
        self.assertIn("content-policy violations", reason)

    def test_clean_policy_merges(self):
        policies = (("migrations/", lambda scoped, h, b: []),)
        verdict, _ = lane(["migrations/011_x.sql"],
                          head_root=".", base_root=".",
                          content_policies=policies)
        self.assertEqual(verdict, "merge")

    def test_policy_only_sees_its_own_prefix(self):
        seen = {}

        def record(scoped, h, b):
            seen["paths"] = list(scoped)
            return []

        verdict, _ = lane(["migrations/011_x.sql", "src/app.py"],
                          head_root=".", base_root=".",
                          content_policies=(("migrations/", record),))
        self.assertEqual(verdict, "merge")
        self.assertEqual(seen["paths"], ["migrations/011_x.sql"])

    def test_out_of_scope_pr_never_invokes_the_policy(self):
        def boom(scoped, h, b):
            raise AssertionError("policy invoked for an out-of-scope PR")
        verdict, _ = lane(["src/app.py"], head_root=".", base_root=".",
                          content_policies=(("migrations/", boom),))
        self.assertEqual(verdict, "merge")

    def test_missing_trees_fail_closed(self):
        policies = (("migrations/", lambda scoped, h, b: []),)
        verdict, reason = lane(["migrations/011_x.sql"],
                               content_policies=policies)  # no roots passed
        self.assertEqual(verdict, "wait")
        self.assertIn("failing closed", reason)

    def test_label_overrides_a_policy_violation(self):
        policies = (("migrations/", lambda scoped, h, b: ["bad statement"]),)
        verdict, _ = lane(["migrations/011_x.sql"], labels=[ds.APPROVAL_LABEL],
                          head_root=".", base_root=".",
                          content_policies=policies)
        self.assertEqual(verdict, "merge")


def _grant(gid="G-20260701-01", **over):
    """A structurally-valid synthetic grant line; override fields per test."""
    entry = {"id": gid, "date": "2026-07-01", "scope": "synthetic test grant",
             "wording": None, "source": "synthetic fixture", "expiry": None,
             "status": "active", "issued_to": "all sessions", "notes": ""}
    entry.update(over)
    return entry


class TestAuthorityGrants(unittest.TestCase):
    """Phase 2 of docs/authority-ledger.md: a cited grant clears a WAIT at
    the two named sites, never a fail, never a protected path."""

    TODAY = __import__("datetime").date(2026, 7, 15)
    VIOLATING = (("migrations/", lambda scoped, h, b: ["bad statement"]),)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base_root = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def _ledger(self, *entries):
        with open(os.path.join(self.base_root, ds.LEDGER_REL_PATH), "w",
                  encoding="utf-8") as fh:
            for e in entries:
                fh.write(json.dumps(e) + "\n")

    def _lane(self, files, body, **kw):
        kw.setdefault("head_root", ".")
        kw.setdefault("base_root", self.base_root)
        kw.setdefault("content_policies", self.VIOLATING)
        kw.setdefault("today", self.TODAY)
        return lane(files, pr_body=body, **kw)

    def test_path_scoped_grant_clears_a_content_policy_wait(self):
        self._ledger(_grant(grant_type="merge-authority",
                            applies_to="content-policy",
                            paths=["migrations/*.sql"]))
        verdict, reason = self._lane(["migrations/011_x.sql"],
                                     "Authority: G-20260701-01")
        self.assertEqual(verdict, "merge")
        self.assertIn("Merged under Authority: G-20260701-01", reason)

    def test_every_changed_file_must_match_the_globs(self):
        self._ledger(_grant(grant_type="merge-authority",
                            applies_to="content-policy",
                            paths=["migrations/*.sql"]))
        verdict, _ = self._lane(["migrations/011_x.sql", "src/app.py"],
                                "Authority: G-20260701-01")
        self.assertEqual(verdict, "wait")

    def test_non_active_and_expired_grants_never_clear(self):
        for over in ({"status": "revoked"}, {"status": "expired"},
                     {"expiry": "2026-07-01"}, {"until": "2026-07-01"}):
            self._ledger(_grant(grant_type="merge-authority",
                                applies_to="content-policy",
                                paths=["migrations/*.sql"], **over))
            verdict, _ = self._lane(["migrations/011_x.sql"],
                                    "Authority: G-20260701-01")
            self.assertEqual(verdict, "wait", over)

    def test_free_text_grant_never_affects_merging(self):
        self._ledger(_grant())  # no grant_type: documentation only
        verdict, _ = self._lane(["migrations/011_x.sql"],
                                "Authority: G-20260701-01")
        self.assertEqual(verdict, "wait")

    def test_defective_ledger_discards_every_grant(self):
        good = _grant(grant_type="merge-authority", applies_to="content-policy",
                      paths=["migrations/*.sql"])
        self._ledger(good, _grant(gid="G-20260701-01"))  # duplicate id
        verdict, _ = self._lane(["migrations/011_x.sql"],
                                "Authority: G-20260701-01")
        self.assertEqual(verdict, "wait")

    def test_no_base_root_consults_no_grants(self):
        verdict, _ = self._lane(["migrations/011_x.sql"],
                                "Authority: G-20260701-01", base_root=None)
        self.assertEqual(verdict, "wait")

    def test_protected_paths_are_never_grant_overridable(self):
        entry = _grant(grant_type="merge-authority", applies_to="content-policy",
                       paths=["*"])
        self.assertFalse(ds.grant_clears_wait(
            ds.GRANT_CONTENT_POLICY, entry,
            [".github/workflows/automerge.yml"], self.TODAY))

    def test_promotion_window_grant_clears_the_promotion_head_wait(self):
        self._ledger(_grant(grant_type="merge-authority", applies_to="promotion",
                            until="2026-07-31"))
        verdict, reason = self._lane(["src/x.py"], "Authority: G-20260701-01",
                                     head="staging", promotion_heads=("staging",),
                                     content_policies=())
        self.assertEqual(verdict, "merge")
        self.assertIn("promotion window 2026-07-01..2026-07-31", reason)

    def test_promotion_grant_outside_its_window_waits(self):
        self._ledger(_grant(grant_type="merge-authority", applies_to="promotion",
                            until="2026-07-31"))
        verdict, _ = self._lane(["src/x.py"], "Authority: G-20260701-01",
                                head="staging", promotion_heads=("staging",),
                                content_policies=(),
                                today=__import__("datetime").date(2026, 8, 2))
        self.assertEqual(verdict, "wait")

    def test_promotion_head_without_grant_or_label_waits(self):
        verdict, reason = self._lane(["src/x.py"], None, head="staging",
                                     promotion_heads=("staging",),
                                     content_policies=())
        self.assertEqual(verdict, "wait")
        self.assertIn("promotion head", reason)

    def test_label_still_releases_the_promotion_lane(self):
        verdict, _ = self._lane(["src/x.py"], None, head="staging",
                                promotion_heads=("staging",),
                                content_policies=(),
                                labels=[ds.APPROVAL_LABEL])
        self.assertEqual(verdict, "merge")


class TestChecksDecision(unittest.TestCase):
    """Phase two: check runs and mergeable state, fail-closed."""

    def test_zero_check_runs_wait(self):
        verdict, reason = ds.checks_decision([], "CLEAN")
        self.assertEqual(verdict, "wait")
        self.assertIn("zero check runs", reason)

    def test_only_the_gates_own_run_still_counts_as_zero(self):
        checks = [{"name": "Auto-merge agent PRs / Squash merge",
                   "status": "completed", "conclusion": "failure"}]
        verdict, _ = ds.checks_decision(checks, "CLEAN")
        self.assertEqual(verdict, "wait")

    def test_failed_earlier_gate_attempt_does_not_deadlock(self):
        checks = GREEN + [{"name": "Auto-merge agent PRs / Squash merge",
                           "status": "completed", "conclusion": "failure"}]
        verdict, _ = ds.checks_decision(checks, "CLEAN")
        self.assertEqual(verdict, "merge")

    def test_superseded_cancelled_run_does_not_poison_the_sha(self):
        # Duplicate workflow events: the same check name carries an old
        # cancelled run and a newer success. Only the newest run counts.
        checks = [dict(c, id=100 + i) for i, c in enumerate(GREEN)] + [
            {"id": 50, "name": "Static checks", "status": "completed",
             "conclusion": "cancelled"},
        ]
        verdict, _ = ds.checks_decision(checks, "CLEAN")
        self.assertEqual(verdict, "merge")

    def test_newer_failure_still_fails_after_dedup(self):
        checks = [{"id": 50, "name": "Static checks", "status": "completed",
                   "conclusion": "success"},
                  {"id": 90, "name": "Static checks", "status": "completed",
                   "conclusion": "failure"}]
        verdict, _ = ds.checks_decision(checks, "CLEAN")
        self.assertEqual(verdict, "fail")

    def test_runs_without_ids_keep_fail_closed_behavior(self):
        # No ids means no ordering; both runs stay and the cancelled one
        # still blocks, exactly the pre-dedup read.
        checks = GREEN + [{"name": "Static checks", "status": "completed",
                           "conclusion": "cancelled"}]
        verdict, _ = ds.checks_decision(checks, "CLEAN")
        self.assertEqual(verdict, "fail")

    def test_failing_check_fails_loud(self):
        checks = [{"name": "Static checks", "status": "completed",
                   "conclusion": "failure"}]
        verdict, reason = ds.checks_decision(checks, "CLEAN")
        self.assertEqual(verdict, "fail")
        self.assertIn("failing", reason)

    def test_cancelled_and_timed_out_also_fail(self):
        for conclusion in ("cancelled", "timed_out", "action_required"):
            checks = GREEN + [{"name": "Extra scan", "status": "completed",
                               "conclusion": conclusion}]
            verdict, _ = ds.checks_decision(checks, "CLEAN")
            self.assertEqual(verdict, "fail", conclusion)

    def test_all_required_green_merges(self):
        verdict, reason = ds.checks_decision(GREEN, "CLEAN")
        self.assertEqual(verdict, "merge")
        self.assertIn("CLEAN", reason)

    def test_missing_required_check_waits(self):
        verdict, reason = ds.checks_decision([GREEN[0]], "CLEAN")
        self.assertEqual(verdict, "wait")
        self.assertIn("no run yet", reason)

    def test_pending_required_check_waits(self):
        checks = [GREEN[0], {"name": "E2E checks", "status": "queued",
                             "conclusion": None}]
        verdict, reason = ds.checks_decision(checks, "CLEAN")
        self.assertEqual(verdict, "wait")
        self.assertIn("not green yet", reason)

    def test_name_match_is_substring_and_case_insensitive(self):
        checks = [
            {"name": "Required checks / static checks (pull_request)",
             "status": "completed", "conclusion": "success"},
            {"name": "Required checks / E2E Checks (pull_request)",
             "status": "completed", "conclusion": "success"},
        ]
        verdict, _ = ds.checks_decision(checks, "CLEAN")
        self.assertEqual(verdict, "merge")

    def test_dirty_merge_state_waits(self):
        verdict, reason = ds.checks_decision(GREEN, "DIRTY")
        self.assertEqual(verdict, "wait")
        self.assertIn("conflict", reason)

    def test_unknown_and_empty_merge_state_wait(self):
        for state in ("UNKNOWN", "", None):
            verdict, _ = ds.checks_decision(GREEN, state)
            self.assertEqual(verdict, "wait", repr(state))


class TestConditionalChecks(unittest.TestCase):
    """Path-conditional required checks mirror the producing workflow."""

    E2E_ONLY = (("Static checks",),
                (("E2E checks", re.compile(r"^static/")),))

    def _decide(self, checks, files):
        always, conditional = self.E2E_ONLY
        return ds.checks_decision(checks, "CLEAN", files,
                                  always_required=always, conditional=conditional)

    def test_relevant_path_requires_the_check(self):
        verdict, reason = self._decide([GREEN[0]], ["static/app.js"])
        self.assertEqual(verdict, "wait")
        self.assertIn("E2E checks", reason)

    def test_irrelevant_path_does_not(self):
        verdict, _ = self._decide([GREEN[0]], ["src/api.py"])
        self.assertEqual(verdict, "merge")

    def test_unlistable_files_make_every_conditional_check_required(self):
        verdict, reason = self._decide([GREEN[0]], None)
        self.assertEqual(verdict, "wait")
        self.assertIn("E2E checks", reason)


class TestCLIContract(unittest.TestCase):
    """The workflow parses a trailing verdict= line; exit code is 0 for
    every computed verdict."""

    def _run(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = ds.main(argv)
        return code, buf.getvalue()

    def test_lane_verdict_line(self):
        code, out = self._run([
            "lane", "--base", "main", "--head", "agent/x",
            "--labels-json", json.dumps([ds.APPROVAL_LABEL]),
            "--draft", "false"])
        self.assertEqual(code, 0)
        self.assertTrue(out.strip().endswith("verdict=merge"))

    def test_lane_wait_exits_green(self):
        # "wait" is a green outcome: the PR is waiting, not broken. A red
        # exit here would make every waiting PR look like a CI failure.
        code, out = self._run([
            "lane", "--base", "main", "--head", "agent/x",
            "--labels-json", "[]", "--draft", "false", "--files-error"])
        self.assertEqual(code, 0)
        self.assertTrue(out.strip().endswith("verdict=wait"))

    def test_checks_verdict_line(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(GREEN, fh)
            checks_file = fh.name
        self.addCleanup(os.unlink, checks_file)
        code, out = self._run([
            "checks", "--checks-json-file", checks_file, "--merge-state", "CLEAN"])
        self.assertEqual(code, 0)
        self.assertTrue(out.strip().endswith("verdict=merge"))


if __name__ == "__main__":
    unittest.main()
