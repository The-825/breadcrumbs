import unittest
from ledger_markdown import cells, source_link


class LedgerMarkdownTests(unittest.TestCase):
    def test_balanced_parentheses_in_doi_are_retained(self):
        value = '["Ironies of Automation"](https://doi.org/10.1016/0005-1098(83)90046-8), 1983'
        self.assertEqual(('Ironies of Automation', 'https://doi.org/10.1016/0005-1098(83)90046-8'), source_link(value))

    def test_nested_and_escaped_parentheses_and_quoted_titles(self):
        self.assertEqual(('A "quoted" title', 'https://example.org/a(b(c))'),
                         source_link(r'["A \"quoted\" title"](https://example.org/a(b(c)))'))
        self.assertEqual(('Pipe | title', 'https://example.org/a(b)'),
                         source_link(r'["Pipe \| title"](https://example.org/a\(b\))'))

    def test_incomplete_or_non_url_links_fail_without_guessing(self):
        for value in ['["Title"](https://example.org/a(b)', '["Title"](javascript:alert(1))', '["Title"](https://example.org/a b)']:
            self.assertEqual((value, ''), source_link(value))

    def test_escaped_pipe_is_not_a_table_boundary(self):
        self.assertEqual(['001', r'One \| two', 'three'], cells(r'| 001 | One \| two | three |'))
