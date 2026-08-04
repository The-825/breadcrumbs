"""Tests for policy_checks.py (merge-time migration content lints).

Every lint bites a deliberately-bad tree and passes a clean one, and every
cannot-inspect corner (missing trees, unparseable ledger) fails closed.
Builds throwaway base/head checkouts in temp dirs so nothing touches the
real folder. Discovered by the same lane as the runner tests:

    python3 -m unittest discover -s ci-kit/migrations/tests
"""
import importlib.util
import os
import shutil
import tempfile
import unittest

_MODULE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "policy_checks.py")


def _load():
    spec = importlib.util.spec_from_file_location("policy_checks", _MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pc = _load()

MIG = "migrations/"

README_LEDGER = (
    "## The claim-first ledger\n\n"
    "**The single current next-free number is `012`** (update this line, and "
    "only this line, when claiming a number).\n")

# Synthetic seed with a generic column shape; the lint keys on the
# enabled/true value, not on any particular schema.
CLEAN_SEED = """\
-- Migration 011_example_flag: seeds the example flag, default OFF.
INSERT INTO feature_flags (name, description, enabled)
VALUES ('example_flag', 'Example seed. Saying DROP TABLE in prose is fine.', FALSE)
ON CONFLICT (name) DO NOTHING;
"""


class TreeFixture(unittest.TestCase):
    """Base/head checkout builder shared by the suites below."""

    def setUp(self):
        self.base_root = tempfile.mkdtemp(prefix="pc-base-")
        self.head_root = tempfile.mkdtemp(prefix="pc-head-")
        self.addCleanup(shutil.rmtree, self.base_root, ignore_errors=True)
        self.addCleanup(shutil.rmtree, self.head_root, ignore_errors=True)
        # Base branch: one existing migration plus the README ledger.
        self._write(self.base_root, MIG + "010_existing_flag.sql", CLEAN_SEED)
        self._write(self.base_root, MIG + "README.md", README_LEDGER)
        # Head starts as a copy of base (the README rides through unedited).
        self._write(self.head_root, MIG + "010_existing_flag.sql", CLEAN_SEED)
        self._write(self.head_root, MIG + "README.md", README_LEDGER)

    def _write(self, root, rel, content):
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)

    def check(self, changed, **kw):
        return pc.policy_violations(changed, self.head_root, self.base_root,
                                    migrations_dir=MIG, **kw)


class TestForwardOnlyLint(TreeFixture):

    def test_clean_new_seed_passes(self):
        self._write(self.head_root, MIG + "011_example_flag.sql", CLEAN_SEED)
        self.assertEqual(self.check([MIG + "011_example_flag.sql"]), [])

    def test_drop_table_blocked(self):
        self._write(self.head_root, MIG + "011_bad.sql", "DROP TABLE tasks;")
        violations = self.check([MIG + "011_bad.sql"])
        self.assertTrue(any("DROP TABLE" in v for v in violations))

    def test_drop_column_blocked(self):
        self._write(self.head_root, MIG + "011_bad.sql",
                    "ALTER TABLE tasks DROP COLUMN note;")
        violations = self.check([MIG + "011_bad.sql"])
        self.assertTrue(any("DROP COLUMN" in v for v in violations))

    def test_truncate_blocked(self):
        self._write(self.head_root, MIG + "011_bad.sql", "TRUNCATE tasks;")
        violations = self.check([MIG + "011_bad.sql"])
        self.assertTrue(any("TRUNCATE" in v for v in violations))

    def test_delete_on_protected_table_blocked(self):
        self._write(self.head_root, MIG + "011_bad.sql",
                    "DELETE FROM warehouse.member_records WHERE 1=1;")
        violations = self.check([MIG + "011_bad.sql"],
                                protected_tables=("member_records",))
        self.assertTrue(any("protected table" in v for v in violations))

    def test_delete_on_ordinary_table_allowed(self):
        # Verified-safe row deletes on operational tables stay label-free;
        # the lint bounds blast radius, it does not ban cleanup.
        self._write(self.head_root, MIG + "011_cleanup.sql",
                    "DELETE FROM feature_flags WHERE name = 'dead_flag';")
        self.assertEqual(self.check([MIG + "011_cleanup.sql"],
                                    protected_tables=("member_records",)), [])

    def test_destructive_words_in_comments_and_strings_ignored(self):
        self._write(self.head_root, MIG + "011_ok.sql",
                    "-- This migration does NOT DROP TABLE anything.\n"
                    "-- A DELETE FROM member_records would be a violation.\n"
                    + CLEAN_SEED)
        self.assertEqual(self.check([MIG + "011_ok.sql"],
                                    protected_tables=("member_records",)), [])


class TestSeedDefaultLint(TreeFixture):

    def test_default_true_blocked(self):
        self._write(self.head_root, MIG + "011_bad_flag.sql",
                    CLEAN_SEED.replace("FALSE", "TRUE", 1))
        violations = self.check([MIG + "011_bad_flag.sql"])
        self.assertTrue(any("enabled/true default" in v for v in violations))

    def test_quoted_true_blocked(self):
        self._write(self.head_root, MIG + "011_bad_flag.sql",
                    CLEAN_SEED.replace("FALSE", "'true'", 1))
        violations = self.check([MIG + "011_bad_flag.sql"])
        self.assertTrue(any("enabled/true default" in v for v in violations))

    def test_override_marker_with_quoted_instruction_allowed(self):
        self._write(self.head_root, MIG + "011_graduated_flag.sql",
                    "-- APPROVED-DEFAULT-ON: <operator> <date>: "
                    "\"turn it on for everyone\"\n"
                    + CLEAN_SEED.replace("FALSE", "TRUE", 1))
        self.assertEqual(self.check([MIG + "011_graduated_flag.sql"]), [])

    def test_unnumbered_snapshot_file_exempt(self):
        # Regenerable re-dump files are records, not migrations; they carry
        # true values legitimately and skip lints 2 and 3 by construction.
        self._write(self.head_root, MIG + "SNAPSHOT_flags_recent.sql",
                    "INSERT INTO feature_flags (name, enabled) VALUES "
                    "('x', 'true') ON CONFLICT (name) DO UPDATE "
                    "SET enabled = EXCLUDED.enabled;")
        self.assertEqual(self.check([MIG + "SNAPSHOT_flags_recent.sql"]), [])


class TestDuplicateNumberGuard(TreeFixture):

    def test_number_taken_on_base_blocked(self):
        self._write(self.head_root, MIG + "010_other_slug.sql", CLEAN_SEED)
        violations = self.check([MIG + "010_other_slug.sql"])
        self.assertTrue(any("already taken" in v for v in violations))

    def test_number_repeated_within_pr_blocked(self):
        self._write(self.head_root, MIG + "011_first.sql", CLEAN_SEED)
        self._write(self.head_root, MIG + "011_second.sql", CLEAN_SEED)
        violations = self.check([MIG + "011_first.sql", MIG + "011_second.sql"])
        self.assertTrue(any("same PR" in v for v in violations))

    def test_unclaimed_number_blocked(self):
        # README next-free is 012; 015 was never claimed.
        self._write(self.head_root, MIG + "015_squatter.sql", CLEAN_SEED)
        violations = self.check([MIG + "015_squatter.sql"])
        self.assertTrue(any("not claimed" in v for v in violations))

    def test_claiming_pr_passes(self):
        # The PR bumps the ledger past its own number in the same PR.
        self._write(self.head_root, MIG + "README.md",
                    README_LEDGER.replace("`012`", "`013`"))
        self._write(self.head_root, MIG + "012_claimed.sql", CLEAN_SEED)
        self.assertEqual(
            self.check([MIG + "012_claimed.sql", MIG + "README.md"]), [])

    def test_unparseable_ledger_fails_closed(self):
        self._write(self.head_root, MIG + "README.md", "no ledger line here\n")
        self._write(self.head_root, MIG + "011_x.sql", CLEAN_SEED)
        violations = self.check([MIG + "011_x.sql", MIG + "README.md"])
        self.assertTrue(any("next-free ledger" in v for v in violations))

    def test_deleting_a_migration_blocked(self):
        os.remove(os.path.join(self.head_root, MIG + "010_existing_flag.sql"))
        violations = self.check([MIG + "010_existing_flag.sql"])
        self.assertTrue(any("deleted or renamed" in v for v in violations))

    def test_editing_an_existing_file_is_content_linted_not_number_checked(self):
        self._write(self.head_root, MIG + "010_existing_flag.sql",
                    CLEAN_SEED + "\nDROP TABLE tasks;")
        violations = self.check([MIG + "010_existing_flag.sql"])
        self.assertTrue(any("DROP TABLE" in v for v in violations))
        self.assertFalse(any("already taken" in v for v in violations))


class TestFailClosed(TreeFixture):

    def test_missing_head_and_base_roots_fail_closed(self):
        violations = pc.policy_violations([MIG + "011_x.sql"], None, None,
                                          migrations_dir=MIG)
        self.assertTrue(any("failing closed" in v for v in violations))

    def test_missing_migrations_dir_on_base_fails_closed(self):
        empty_base = tempfile.mkdtemp(prefix="pc-empty-")
        self.addCleanup(shutil.rmtree, empty_base, ignore_errors=True)
        violations = pc.policy_violations([MIG + "011_x.sql"],
                                          self.head_root, empty_base,
                                          migrations_dir=MIG)
        self.assertTrue(any("failing closed" in v for v in violations))

    def test_non_sql_changes_carry_no_sql_policy(self):
        self._write(self.head_root, MIG + "README.md",
                    README_LEDGER + "\nextra prose\n")
        self.assertEqual(self.check([MIG + "README.md"]), [])


if __name__ == "__main__":
    unittest.main()


class TestSlugEra(TreeFixture):
    """Lint 4: the timestamp-slug namespace and the era switch."""

    SLUG = MIG + "20260722_1405_example_flag.sql"

    def test_slug_file_skips_the_numbering_checks(self):
        # No claim, no ledger read: a mint-dated key has nothing to race.
        self._write(self.head_root, self.SLUG, CLEAN_SEED)
        self.assertEqual(self.check([self.SLUG]), [])

    def test_slug_file_still_gets_the_content_lints(self):
        bad = CLEAN_SEED.replace("FALSE", "TRUE")
        self._write(self.head_root, self.SLUG, bad)
        violations = self.check([self.SLUG])
        self.assertEqual(len(violations), 1)
        self.assertIn("enabled/true default", violations[0])

    def test_enacted_era_blocks_a_new_numbered_file(self):
        self._write(self.head_root, MIG + "011_late_arrival.sql", CLEAN_SEED)
        violations = self.check([MIG + "011_late_arrival.sql"],
                                slug_era_enacted=True,
                                numbered_era_closed_at=10)
        self.assertEqual(len(violations), 1)
        self.assertIn("closed at 10", violations[0])
        self.assertIn("YYYYMMDD_HHMM_<slug>", violations[0])

    def test_enacted_era_leaves_legacy_numbered_edits_alone(self):
        # 010 exists on base: editing it is content-checked only, never
        # renamed, never re-gated by the namespace guard.
        self._write(self.head_root, MIG + "010_existing_flag.sql",
                    CLEAN_SEED + "\n-- annotated\n")
        self.assertEqual(self.check([MIG + "010_existing_flag.sql"],
                                    slug_era_enacted=True), [])

    def test_default_era_is_open_and_numbered_flow_unchanged(self):
        self.assertFalse(pc.SLUG_ERA_ENACTED)
        self._write(self.head_root, MIG + "011_next_claimed.sql", CLEAN_SEED)
        self.assertEqual(self.check([MIG + "011_next_claimed.sql"]), [])
