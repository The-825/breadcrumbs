#!/usr/bin/env python3
"""Self-tests for the memory desk's mem CLI.

Run from anywhere: python3 templates/memory-desk/tests/test_mem.py
Subprocess-driven end to end: each test runs the real executable against a
throwaway desk in a temp directory, so the contract under test (exit codes
included) is the one a session actually gets. The last class runs the shipped
kit itself through its own integrity gate, so the template cannot rot without
failing the build that carries it.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
MEM = KIT / "mem"


def run(args, cwd, stdin=None):
    return subprocess.run(
        [sys.executable, str(Path(cwd) / "mem"), *args],
        input=stdin, capture_output=True, text=True, cwd=cwd,
    )


FIXTURE_INDEX = "\n".join([
    "# fixture index",
    "deploy gate\trelease check|ship gate\tmerges wait for the approval label; CI green is not enough\tREADME.md\t2026-08-08",
    "retry budget\t\tpush retries cap at four with exponential backoff\tREADME.md\t-",
    "log format\tlogging|log lines\tone JSON object per line, ts first\tREADME.md\t2020-01-01",
]) + "\n"


class DeskFixture(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="memdesk-"))
        shutil.copy2(MEM, self.dir / "mem")
        (self.dir / "index.tsv").write_text(FIXTURE_INDEX, encoding="utf-8")
        (self.dir / "MEMORY.md").write_text("# kernel\n", encoding="utf-8")
        (self.dir / "README.md").write_text("fixture\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def append_row(self, row):
        with (self.dir / "index.tsv").open("a", encoding="utf-8") as f:
            f.write(row + "\n")


class TestLookup(DeskFixture):
    def test_exact_key_hit(self):
        r = run(["deploy", "gate"], self.dir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("approval label", r.stdout)
        self.assertIn("source: README.md", r.stdout)

    def test_alias_hit(self):
        r = run(["ship", "gate"], self.dir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("approval label", r.stdout)

    def test_ranked_fallback_hit(self):
        r = run(["what", "is", "the", "retry", "policy"], self.dir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("exponential backoff", r.stdout)

    def test_stale_row_is_flagged(self):
        r = run(["log", "format"], self.dir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("STALE", r.stdout)

    def test_default_horizon_is_30_not_90(self):
        # Fewer than STALE_SAMPLE_MIN dated rows, so this falls back to the
        # default rather than adapting. A row checked 40 days ago is stale
        # under the new 30-day default and would NOT have been under the
        # old fixed 90-day one, this is the regression proof that the
        # default actually moved.
        checked_40d_ago = (datetime.now(timezone.utc) - timedelta(days=40)).strftime("%Y-%m-%d")
        index = "\n".join([
            "# fixture index",
            f"only entry\t\tan answer\tREADME.md\t{checked_40d_ago}",
        ]) + "\n"
        (self.dir / "index.tsv").write_text(index, encoding="utf-8")
        r = run(["only", "entry"], self.dir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("STALE", r.stdout)
        self.assertIn("30d horizon", r.stdout)

    def test_adaptive_horizon_shortens_for_a_fast_moving_ledger(self):
        # Several rows re-checked every ~5 days recently: median gap 5 * 3
        # grace = 15, clamped to STALE_FLOOR (14). A target row checked 20
        # days ago is stale under that 15-day adapted horizon, but would
        # NOT be under the 30-day default, proving the horizon actually
        # moved with the ledger's own cadence, not just a static fallback.
        now = datetime.now(timezone.utc)
        rows = ["# fixture index"]
        for i, days_ago in enumerate([5, 10, 15, 20, 25]):
            d = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            rows.append(f"cadence row {i}\t\tan answer\tREADME.md\t{d}")
        target_checked = (now - timedelta(days=20)).strftime("%Y-%m-%d")
        rows.append(f"target row\t\tan answer\tREADME.md\t{target_checked}")
        (self.dir / "index.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
        r = run(["target", "row"], self.dir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("STALE", r.stdout)
        self.assertIn("15d horizon", r.stdout)

    def test_adaptive_horizon_lengthens_for_a_quiet_ledger_but_caps_at_ceiling(self):
        # Rows re-checked every ~60 days: median gap 60 * 3 = 180, clamped
        # to STALE_CEILING (90). A target row checked 50 days ago is NOT
        # stale under the 90-day adapted horizon, though it WOULD be under
        # the 30-day default, proving both the lengthening and the clamp.
        now = datetime.now(timezone.utc)
        rows = ["# fixture index"]
        for i, days_ago in enumerate([60, 120, 180]):
            d = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            rows.append(f"quiet row {i}\t\tan answer\tREADME.md\t{d}")
        target_checked = (now - timedelta(days=50)).strftime("%Y-%m-%d")
        rows.append(f"target row\t\tan answer\tREADME.md\t{target_checked}")
        (self.dir / "index.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
        r = run(["target", "row"], self.dir)
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("STALE", r.stdout)
        self.assertIn("90d horizon", r.stdout)

    def test_miss_exits_one_and_prints_the_ladder(self):
        r = run(["quantum", "router"], self.dir)
        self.assertEqual(r.returncode, 1)
        self.assertIn("no index hit", r.stdout)
        self.assertIn("grep -ril 'quantum'", r.stdout)
        self.assertIn("mem add", r.stdout)

    def test_stdin_hook_mode_is_quiet_on_miss(self):
        r = run(["--stdin"], self.dir, stdin="tell me about quantum routers")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "")

    def test_stdin_hook_mode_hits_on_overlap(self):
        r = run(["--stdin"], self.dir, stdin="how do we handle the deploy gate here")
        self.assertEqual(r.returncode, 0)
        self.assertIn("approval label", r.stdout)

    def test_no_args_prints_the_card(self):
        r = run([], self.dir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("one door", r.stdout)


class TestAdd(DeskFixture):
    def test_add_appends_a_valid_entry(self):
        r = run(["add", "the cache ttl is one hour", "--type", "fact", "--source", "README.md"], self.dir)
        self.assertEqual(r.returncode, 0)
        lines = (self.dir / "journal.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        entry = json.loads(lines[0])
        self.assertEqual(entry["type"], "fact")
        self.assertEqual(entry["text"], "the cache ttl is one hour")
        self.assertEqual(entry["source"], "README.md")
        self.assertIn("ts", entry)

    def test_add_rejects_unknown_type(self):
        r = run(["add", "something", "--type", "vibe"], self.dir)
        self.assertEqual(r.returncode, 2)

    def test_add_rejects_empty_text(self):
        r = run(["add", "--type", "fact"], self.dir)
        self.assertEqual(r.returncode, 2)


class TestCheck(DeskFixture):
    def test_clean_fixture_passes(self):
        r = run(["check"], self.dir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("memory ok", r.stdout)

    def test_duplicate_key_fails(self):
        self.append_row("Deploy Gate\t\tanother answer\tREADME.md\t-")
        r = run(["check"], self.dir)
        self.assertEqual(r.returncode, 2)
        self.assertIn("collides", r.stdout)

    def test_dead_source_fails(self):
        self.append_row("orphan fact\t\tan answer\tmissing.md\t-")
        r = run(["check"], self.dir)
        self.assertEqual(r.returncode, 2)
        self.assertIn("resolves nowhere", r.stdout)

    def test_reserved_key_word_fails(self):
        self.append_row("check the gate\t\tan answer\tREADME.md\t-")
        r = run(["check"], self.dir)
        self.assertEqual(r.returncode, 2)
        self.assertIn("reserved", r.stdout)

    def test_oversized_kernel_fails(self):
        (self.dir / "MEMORY.md").write_text("line\n" * 61, encoding="utf-8")
        r = run(["check"], self.dir)
        self.assertEqual(r.returncode, 2)
        self.assertIn("cap is 60", r.stdout)

    def test_malformed_journal_line_fails(self):
        (self.dir / "journal.jsonl").write_text("not json\n", encoding="utf-8")
        r = run(["check"], self.dir)
        self.assertEqual(r.returncode, 2)
        self.assertIn("journal.jsonl", r.stdout)

    def test_malformed_row_fails(self):
        self.append_row("only three\tfields\there")
        r = run(["check"], self.dir)
        self.assertEqual(r.returncode, 2)
        self.assertIn("want 5", r.stdout)


class TestShippedKit(unittest.TestCase):
    """The template ships holding its own bar: the seeded index, the kernel
    template, and the self-describing rows all pass the gate they document."""

    def test_shipped_desk_passes_check(self):
        r = run(["check"], KIT)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("memory ok", r.stdout)

    def test_shipped_lookup_answers_capture_question(self):
        r = run(["capture", "a", "fact"], KIT)
        self.assertEqual(r.returncode, 0)
        self.assertIn("mem add", r.stdout)

    def test_shipped_lookup_answers_grep_fallback(self):
        r = run(["--stdin"], KIT, stdin="what do I do when mem is unavailable")
        self.assertEqual(r.returncode, 0)
        self.assertIn("grep -i", r.stdout)


class TestReject(DeskFixture):
    """The must-not-come-back test: retiring an answer has to actually stop it."""

    def retire(self, key="deploy gate", reason="the label rule changed"):
        return run(["reject", key, "--reason", reason], self.dir)

    def test_reject_removes_the_row_and_writes_a_tombstone(self):
        r = self.retire()
        self.assertEqual(r.returncode, 0)
        self.assertIn("retired", r.stdout)
        self.assertNotIn("deploy gate", (self.dir / "index.tsv").read_text(encoding="utf-8"))
        tomb = (self.dir / "tombstones.tsv").read_text(encoding="utf-8")
        self.assertIn("deploy gate", tomb)
        self.assertIn("the label rule changed", tomb)

    def test_reject_requires_a_reason(self):
        r = run(["reject", "deploy gate"], self.dir)
        self.assertEqual(r.returncode, 2)
        self.assertIn("--reason", r.stderr)

    def test_reject_on_a_missing_key_is_a_miss_not_a_crash(self):
        r = run(["reject", "no such key", "--reason", "x"], self.dir)
        self.assertEqual(r.returncode, 1)

    def test_same_answer_returning_fails_check(self):
        self.retire()
        self.append_row(
            "deploy gate\t\tmerges wait for the approval label; CI green is not enough"
            "\tREADME.md\t2026-08-20"
        )
        r = run(["check"], self.dir)
        self.assertEqual(r.returncode, 2)
        self.assertIn("is back carrying the answer retired", r.stdout)

    def test_a_different_answer_for_the_same_key_passes(self):
        """A correction is the whole point; only the retired VALUE is barred."""
        self.retire()
        self.append_row("deploy gate\t\ttwo approvals now, not one\tREADME.md\t2026-08-20")
        r = run(["check"], self.dir)
        self.assertEqual(r.returncode, 0)

    def test_looking_up_a_retired_key_reports_the_retirement(self):
        self.retire()
        r = run(["deploy", "gate"], self.dir)
        self.assertEqual(r.returncode, 1)
        self.assertIn("RETIRED", r.stdout)
        self.assertIn("the label rule changed", r.stdout)

    def test_retirement_does_not_preempt_an_unrelated_query(self):
        """A tombstone answers its own key only, never a fuzzy neighbour."""
        self.retire()
        r = run(["retry", "budget"], self.dir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("exponential backoff", r.stdout)
        self.assertNotIn("RETIRED", r.stdout)

    def test_hook_mode_never_emits_a_retirement(self):
        """Hook mode stays silent on misses; a retirement is still a miss."""
        self.retire()
        r = run(["--stdin"], self.dir, stdin="deploy gate")
        self.assertNotIn("RETIRED", r.stdout)


class TestRecheck(DeskFixture):
    """Drift by evidence rather than by calendar."""

    def test_source_changed_after_check_is_reported(self):
        self.append_row("stale row\t\tan answer whose source moved\tREADME.md\t2020-01-01")
        r = run(["recheck"], self.dir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("stale row", r.stdout)

    def test_reports_suspicion_not_a_verdict(self):
        """The wording matters: a moved source is a prompt to look, not a failure."""
        self.append_row("stale row\t\tan answer whose source moved\tREADME.md\t2020-01-01")
        r = run(["recheck"], self.dir)
        self.assertIn("re-read the source", r.stdout)

    def test_recheck_never_fails_the_build(self):
        r = run(["recheck"], self.dir)
        self.assertEqual(r.returncode, 0)

    def test_undated_rows_are_not_reported_as_drifted(self):
        """A row checked '-' has no baseline to drift from."""
        r = run(["recheck"], self.dir)
        self.assertNotIn("retry budget", r.stdout)


class TestReservedWords(DeskFixture):
    def test_new_subcommands_are_reserved_as_key_prefixes(self):
        self.append_row("reject a thing\t\tsome answer\tREADME.md\t2026-08-20")
        r = run(["check"], self.dir)
        self.assertEqual(r.returncode, 2)
        self.assertIn("reserved subcommand word", r.stdout)


if __name__ == "__main__":
    unittest.main()
