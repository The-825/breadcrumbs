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


if __name__ == "__main__":
    unittest.main()
