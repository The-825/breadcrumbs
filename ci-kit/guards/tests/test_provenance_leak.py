"""Tests for the provenance-leak guard.

This guard is the odd one on the shelf: the others take a file path, this one
takes text, because the thing it screens is a commit message or a PR body
rather than a file in the tree. So it gets its own test module and imports the
functions directly instead of running the script against a fixture.

The two cases that matter most are the last two: ordinary technical prose has
to pass. A guard on your commit messages that fires on normal engineering
sentences gets disabled within a week, and then you have no guard.
"""
import importlib.util
import os
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_GUARD = os.path.join(os.path.dirname(_HERE), "guard_no_provenance_leak.py")

_spec = importlib.util.spec_from_file_location("guard_no_provenance_leak", _GUARD)
guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(guard)

TERMS = ["Acme", "Northwind"]


class TestPrivateTerms(unittest.TestCase):
    def test_term_is_caught(self):
        self.assertTrue(guard.scan("ported from Acme", TERMS))

    def test_case_does_not_rescue_a_term(self):
        self.assertTrue(guard.scan("PORTED FROM acme", TERMS))

    def test_substring_is_not_a_hit(self):
        self.assertFalse(guard.scan("Acmeter readings", TERMS))

    def test_second_term_is_caught(self):
        self.assertTrue(guard.scan("see the Northwind export", TERMS))


class TestScrubNarration(unittest.TestCase):
    """These fire with no wordlist at all, which is the point: the act of
    scrubbing is a tell even when the subject is never named."""

    def test_deidentified(self):
        self.assertTrue(guard.scan("de-identified the sample", []))

    def test_scrubbed(self):
        self.assertTrue(guard.scan("scrubbed the fixtures", []))

    def test_generalized_from(self):
        self.assertTrue(guard.scan("generalized from our system", []))

    def test_private_repo(self):
        self.assertTrue(guard.scan("mirrored from the private repo", []))

    def test_removed_the_employer_example(self):
        self.assertTrue(guard.scan("removed the employer example", []))


class TestOrdinaryProsePasses(unittest.TestCase):
    def test_normal_fix_message(self):
        self.assertFalse(
            guard.scan("fix: guard missed underscored names; add regression test", TERMS)
        )

    def test_naming_a_real_defect_passes(self):
        self.assertFalse(
            guard.scan("fix: the check reported clean when it had not run", TERMS)
        )

    def test_feature_message(self):
        self.assertFalse(
            guard.scan("feat: preflight reports SKIPPED when it cannot run", TERMS)
        )


class TestReporting(unittest.TestCase):
    def test_clean_text_exits_zero(self):
        self.assertEqual(guard.report([], "test"), 0)

    def test_a_hit_exits_one(self):
        self.assertEqual(guard.report([("private-term", "Acme")], "test"), 1)


class TestTermsFile(unittest.TestCase):
    def test_comments_and_blanks_are_ignored(self):
        path = os.path.join(_HERE, "_terms_tmp")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("# a comment\n\nAcme\nNorthwind  # trailing\n")
        try:
            self.assertEqual(guard.load_terms(path), ["Acme", "Northwind"])
        finally:
            os.remove(path)

    def test_missing_file_raises_rather_than_passing(self):
        with self.assertRaises(OSError):
            guard.load_terms(os.path.join(_HERE, "_no_such_terms_file"))


if __name__ == "__main__":
    unittest.main()
