import copy
import unittest

import build_discovery as discovery


class PromptCatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = discovery.read(discovery.DOCS / 'prompt-library.json')

    def test_current_templates_cover_requested_categories_without_model_claims(self):
        rows = discovery.prompt_catalog(self.catalog)
        self.assertEqual({'workflows', 'data-stacks', 'systems'}, {row['category'] for row in rows})
        self.assertTrue(all(row['model_evaluation'] == 'not-run' for row in rows))
        self.assertTrue(all(row['authority'] == 'descriptive-only' for row in rows))

    def test_missing_extra_and_duplicate_input_contracts_fail(self):
        for operation in ('missing-example', 'extra-example', 'duplicate-field', 'missing-placeholder'):
            with self.subTest(operation=operation):
                changed = copy.deepcopy(self.catalog)
                row = changed['prompts'][0]
                field = row['required_inputs'][0]
                if operation == 'missing-example':
                    row['sample_inputs'].pop(field)
                elif operation == 'extra-example':
                    row['sample_inputs']['UNDECLARED'] = 'synthetic'
                elif operation == 'duplicate-field':
                    row['required_inputs'].append(field)
                else:
                    row['template'] = row['template'].replace('{{' + field + '}}', '')
                with self.assertRaisesRegex(ValueError, 'fields do not match'):
                    discovery.prompt_catalog(changed)

    def test_duplicate_ids_and_unreviewed_evaluation_or_authority_fail(self):
        changed = copy.deepcopy(self.catalog)
        changed['prompts'].append(changed['prompts'][0])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            discovery.prompt_catalog(changed)
        for field, value in [('authority', 'execute'), ('model_evaluation', 'passed')]:
            changed = copy.deepcopy(self.catalog)
            changed['prompts'][0][field] = value
            with self.assertRaisesRegex(ValueError, 'reviewed contract'):
                discovery.prompt_catalog(changed)

    def test_unsafe_sources_and_missing_checks_fail(self):
        changed = copy.deepcopy(self.catalog)
        changed['prompts'][0]['source_urls'] = ['javascript:alert(1)']
        with self.assertRaises(ValueError):
            discovery.prompt_catalog(changed)
        for field in ('output_checks', 'limitations', 'source_urls'):
            changed = copy.deepcopy(self.catalog)
            changed['prompts'][0][field] = []
            with self.assertRaisesRegex(ValueError, 'boundaries'):
                discovery.prompt_catalog(changed)
