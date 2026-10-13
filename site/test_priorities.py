import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import build_priorities as priorities


class PriorityTests(unittest.TestCase):
    def test_existing_projection_and_view_reproduce_without_editorial_changes(self):
        old = json.loads((priorities.DOCS / 'staletoast-appraisal-priorities.json').read_text(encoding='utf-8'))
        actual = priorities.build(priorities.DOCS, old['date'])
        self.assertEqual(old, actual)
        self.assertEqual((priorities.DOCS / 'staletoast-appraisal-priorities.md').read_text(encoding='utf-8'), priorities.render(actual))

    def fixture(self, root, extra='', app_extra=''):
        values = {
            'research_source_sha256': '## Source ledger\n| 001 | ["One"](https://example.org/one) | scope | finding | impact | limit |\n' + extra + '### Entry metadata\n| 001 | repeated metadata | a | b | c |\n',
            'appraisal_source_sha256': '| 001 | design | D2 adjacent | SYNTHETIC | single | limits | CI-006 |\n' + app_extra,
            'repository_source_sha256': json.dumps({'repositories': []}),
        }
        for field, text in values.items():
            (root / priorities.SOURCES[field]).write_text(text, encoding='utf-8')

    def test_growth_escaped_pipes_and_candidate_depth_come_from_owning_sources(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root,
                         '| C-025 | ["Recovery \\| review"](https://example.org/two) | scope | finding | impact | limit | candidate |\n',
                         '| C-025 | design | D2 adjacent | SYNTHETIC | single | selected-full-text: bounded review | CI-006 |\n')
            actual = priorities.build(root, '2026-10-13')
            rows = actual['research']
            self.assertEqual(2, len(rows))
            self.assertEqual('Recovery | review', rows[1]['title'])
            self.assertEqual('selected-full-text', rows[1]['review_depth'])
            self.assertEqual('candidate-not-promoted', rows[1]['record_state'])
            self.assertEqual(rows[0]['appraisal_priority_rank'], rows[1]['appraisal_priority_rank'])
            self.assertIn('Recovery \\| review', priorities.render(actual))

    def test_missing_appraisal_duplicate_and_malformed_rows_fail(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root, '| C-025 | ["Two"](https://example.org/two) | a | b | c | d | e |\n')
            with self.assertRaisesRegex(ValueError, 'IDs do not match'):
                priorities.build(root, '2026-10-13')
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            priorities.identified_rows('| 001 | a |\n| 001 | b |', {2})
        with self.assertRaisesRegex(ValueError, 'malformed'):
            priorities.identified_rows('| 001 | a |', {7})

    def test_unknown_claim_fails_and_empty_claims_do_not_gain_priority(self):
        with self.assertRaisesRegex(ValueError, 'unknown claim'):
            priorities.claim_priority(['CI-999'])
        self.assertEqual(len(priorities.GAPS), priorities.claim_priority([]))

    def test_crlf_and_lf_sources_produce_identical_hashes_and_priorities(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            first = priorities.build(root, '2026-10-13')
            for name in priorities.SOURCES.values():
                path = root / name
                path.write_bytes(path.read_text(encoding='utf-8').encode('utf-8').replace(b'\n', b'\r\n'))
            self.assertEqual(first, priorities.build(root, '2026-10-13'))


if __name__ == '__main__':
    unittest.main()
