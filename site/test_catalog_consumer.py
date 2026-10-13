import copy
import hashlib
import json
import unittest

import catalog_consumer as consumer


class CatalogConsumerTests(unittest.TestCase):
    def fixture(self):
        payload = dict(schema_version='1.0', canonical_owner='The-825/staletoast',
                       authority='evidence-only', source_revision='a' * 40,
                       catalogs={name: [{'id': name + '-1'}] for name in ('research', 'repositories', 'claims')})
        payload['catalogs']['charts'] = {'latest': {'edition_date': '2026-10-13'}, 'history': [{'edition_date': '2026-10-13'}]}
        raw = json.dumps(payload).encode('utf-8')
        config = dict(url=consumer.EXPORT_BASE + 'a' * 40 + '.json', canonical_owner='The-825/staletoast',
                      source_revision='a' * 40, sha256=hashlib.sha256(raw).hexdigest())
        return payload, raw, config

    def test_reviewed_pin_accepts_and_changed_bytes_fail(self):
        payload, raw, config = self.fixture()
        self.assertEqual(payload, consumer.validate_export(raw, config))
        with self.assertRaisesRegex(ValueError, 'digest'):
            consumer.validate_export(raw + b' ', config)

    def test_revision_owner_authority_and_duplicate_identity_fail_even_with_matching_digest(self):
        payload, _, config = self.fixture()
        for field, value in [('source_revision', 'b' * 40), ('canonical_owner', 'example/other'), ('authority', 'execute')]:
            changed = copy.deepcopy(payload)
            changed[field] = value
            raw = json.dumps(changed).encode('utf-8')
            config['sha256'] = hashlib.sha256(raw).hexdigest()
            with self.assertRaises(ValueError):
                consumer.validate_export(raw, config)
        payload['catalogs']['research'] *= 2
        raw = json.dumps(payload).encode('utf-8')
        config['sha256'] = hashlib.sha256(raw).hexdigest()
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            consumer.validate_export(raw, config)

    def test_companion_ownership_and_noncanonical_fetch_are_rejected(self):
        payload, raw, config = self.fixture()
        config['url'] = 'https://example.org/catalog.json'
        with self.assertRaisesRegex(ValueError, 'canonical'):
            consumer.validate_export(raw, config)
        config['url'] = consumer.EXPORT_BASE + 'a' * 40 + '.json'
        payload['catalogs']['prompts'] = []
        raw = json.dumps(payload).encode('utf-8')
        config['sha256'] = hashlib.sha256(raw).hexdigest()
        with self.assertRaisesRegex(ValueError, 'ownership'):
            consumer.validate_export(raw, config)


if __name__ == '__main__':
    unittest.main()
