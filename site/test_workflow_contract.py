import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('workflow_registry', ROOT / 'scripts/workflow_registry.py')
registry_tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(registry_tool)


class WorkflowSourceTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT / 'docs/workflow-registry.json').read_text(encoding='utf-8'))
        self.routing = json.loads((ROOT / 'docs/jarvis-workflow-routing.json').read_text(encoding='utf-8'))

    def primary(self):
        self.registry['schema_version'] = '1.1'
        for row in self.registry['workflows']:
            row['source_pin'] = dict(canonical_url=row['source_url'], version='synthetic revision',
                                     retrieved_date='2026-10-13', content_sha256='a' * 64, license_status='unknown')
        row = self.registry['workflows'][0]
        row.update(source_type='official-documentation', source_url='https://example.org/workflow')
        row['source_pin']['canonical_url'] = row['source_url']
        return row

    def test_current_registry_keeps_its_v1_contract(self):
        self.assertEqual([], registry_tool.validate(self.registry, self.routing))
        self.registry['workflows'][0]['source_url'] = 'https://example.org/workflow'
        self.assertTrue(any('schema 1.0' in error for error in registry_tool.validate(self.registry, self.routing)))

    def test_v11_accepts_pinned_primary_source_without_granting_authority(self):
        self.primary()
        self.assertEqual([], registry_tool.validate(self.registry, self.routing))
        self.assertTrue(all(row['authority'] == 'descriptive-only' for row in self.registry['workflows']))

    def test_existing_community_rows_can_migrate_without_invented_source_pins(self):
        self.registry['schema_version'] = '1.1'
        self.assertEqual([], registry_tool.validate(self.registry, self.routing))

    def test_digest_version_date_license_and_canonical_url_are_required(self):
        row = self.primary()
        for field in ('canonical_url', 'version', 'retrieved_date', 'content_sha256', 'license_status'):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.registry)
                changed['workflows'][0]['source_pin'].pop(field)
                self.assertTrue(registry_tool.validate(changed, self.routing))
        row['source_pin']['retrieved_date'] = '20261013'
        self.assertTrue(registry_tool.validate(self.registry, self.routing))

    def test_unsafe_sources_and_disguised_community_posts_fail(self):
        row = self.primary()
        for url in ('http://example.org/workflow', 'javascript:alert(1)', 'https://user:password@example.org/workflow', 'https://www.reddit.com.evil.example/workflow'):
            row.update(source_type='community-post', source_url=url)
            self.assertTrue(registry_tool.source_errors(row, '1.1'))

    def test_publication_does_not_substitute_for_reproduction_or_adoption(self):
        row = self.primary()
        row.pop('reproduction')
        self.assertTrue(any('passing check' in error for error in registry_tool.validate(self.registry, self.routing)))
        row['adoption_state'] = 'adopted'
        self.assertTrue(any('adoption needs' in error for error in registry_tool.validate(self.registry, self.routing)))


if __name__ == '__main__':
    unittest.main()
