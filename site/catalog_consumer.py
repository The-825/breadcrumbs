"""Consume one pinned StaleToast export; never fall back to an owning ledger."""
import hashlib
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'staletoast-consumer.json'
CACHE = ROOT / 'site/data/staletoast-export.json'
EXPORT_BASE = 'https://the-825.github.io/staletoast/exports/'
MAX_BYTES = 10 * 1024 * 1024


def validate_export(raw, config):
    expected_url = EXPORT_BASE + config.get('source_revision', '') + '.json'
    if config.get('url') != expected_url or config.get('canonical_owner') != 'The-825/staletoast':
        raise ValueError('catalog consumer must use the canonical StaleToast export')
    if not re.fullmatch(r'[0-9a-f]{40}', config.get('source_revision', '')):
        raise ValueError('catalog export requires a pinned source revision')
    if not re.fullmatch(r'[0-9a-f]{64}', config.get('sha256', '')):
        raise ValueError('catalog export requires a pinned digest')
    if len(raw) > MAX_BYTES or hashlib.sha256(raw).hexdigest() != config['sha256']:
        raise ValueError('catalog export digest or size differs from the reviewed pin')
    payload = json.loads(raw)
    if payload.get('schema_version') != '1.0' or payload.get('canonical_owner') != 'The-825/staletoast':
        raise ValueError('catalog export owner or schema differs')
    if payload.get('authority') != 'evidence-only' or payload.get('source_revision') != config['source_revision']:
        raise ValueError('catalog export authority or revision differs')
    catalogs = payload.get('catalogs', {})
    if set(catalogs) != {'research', 'repositories', 'claims', 'charts'}:
        raise ValueError('catalog export must keep workflow and prompt ownership separate')
    for name in ('research', 'repositories', 'claims'):
        rows = catalogs[name]
        if not isinstance(rows, list) or not rows:
            raise ValueError('catalog export has missing records')
        ids = [row.get('id') if isinstance(row, dict) else None for row in rows]
        if any(not isinstance(identity, str) or not identity for identity in ids) or len(set(ids)) != len(ids):
            raise ValueError('catalog export has duplicate or invalid identities')
    charts = catalogs['charts']
    if not isinstance(charts, dict) or not charts.get('history') or not charts.get('latest'):
        raise ValueError('catalog export has no dated chart history')
    return payload


def load_export():
    config = json.loads(CONFIG.read_text(encoding='utf-8'))
    if not re.fullmatch(r'[0-9a-f]{40}', config.get('source_revision', '')) or not re.fullmatch(r'[0-9a-f]{64}', config.get('sha256', '')):
        raise ValueError('catalog consumer needs a reviewed revision and digest')
    cache = CACHE.with_name('staletoast-export-' + config['sha256'] + '.json')
    if cache.exists():
        return validate_export(cache.read_bytes(), config)
    export_url = EXPORT_BASE + config.get('source_revision', '') + '.json'
    if config.get('url') != export_url:
        raise ValueError('catalog consumer URL is not canonical')
    request = urllib.request.Request(export_url, headers={'User-Agent': 'Breadcrumbs-pinned-catalog-consumer'})
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read(MAX_BYTES + 1)
    payload = validate_export(raw, config)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(raw)
    return payload


if __name__ == '__main__':
    data = load_export()
    print('catalog consumer: verified StaleToast ' + data['source_revision'])
