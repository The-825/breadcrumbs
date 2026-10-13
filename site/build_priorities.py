"""Rebuild editorial appraisal priorities from public ledgers using Python 3 only."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from ledger_markdown import cells, source_link

DOCS = Path(__file__).resolve().parents[1] / "docs"
SOURCES = {
    "research_source_sha256": "collaborative-intelligence-research-ledger.md",
    "appraisal_source_sha256": "collaborative-intelligence-source-appraisals.md",
    "repository_source_sha256": "collaborative-intelligence-repository-landscape.json",
}
GAPS = ['CI-006', 'CI-007', 'CI-008', 'CI-009', 'CI-004', 'CI-017', 'CI-001',
        'CI-002', 'CI-010', 'CI-011', 'CI-016', 'CI-012', 'CI-015', 'CI-003',
        'CI-005', 'CI-013', 'CI-014']
QUESTION = "Which evidence reduces uncertainty about handoff recovery, authority, revision-sensitive memory, and total evaluation burden?"
IDENTITY = re.compile(r"(?:\d{3}|C-\d{3})")


def identified_rows(text, widths):
    rows = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        row = cells(line)
        if not IDENTITY.fullmatch(row[0]):
            continue
        if len(row) not in widths:
            raise ValueError(f"{row[0]}: malformed source row")
        if row[0] in rows:
            raise ValueError(f"{row[0]}: duplicate source ID")
        rows[row[0]] = row
    return rows


def rank(rows, key):
    rows.sort(key=lambda row: (key(row), row['id']))
    previous, group = None, 0
    for row in rows:
        current = key(row)
        if current != previous:
            group += 1
            previous = current
        row.update(appraisal_priority_rank=group, priority_key=list(current),
                   priority_claim=GAPS[current[0]] if current[0] < len(GAPS) else 'unknown')
    return rows


def claim_priority(claims):
    unknown = set(claims) - set(GAPS)
    if unknown:
        raise ValueError(f"unknown claim IDs: {sorted(unknown)}")
    return min((GAPS.index(claim) for claim in claims), default=len(GAPS))


def build(docs, as_of):
    if date.fromisoformat(as_of).isoformat() != as_of:
        raise ValueError("date must use YYYY-MM-DD")
    texts = {field: (docs / name).read_text(encoding='utf-8') for field, name in SOURCES.items()}
    ledger = texts['research_source_sha256']
    # Metadata repeats IDs and is not a second source record.
    ledger = ledger.split('## Source ledger', 1)[1].split('### Entry metadata', 1)[0]
    sources = identified_rows(ledger, {6, 7})
    appraisals = identified_rows(texts['appraisal_source_sha256'], {7, 8})
    if set(sources) != set(appraisals):
        raise ValueError("research and appraisal IDs do not match")
    research = []
    directness = {'D3': 0, 'D2': 1, 'D1': 2, 'D0': 3}
    horizons = {'longitudinal': 0, 'repeated': 1, 'single': 2, 'technical': 3,
                'retrospective': 4, 'not observed': 5, 'short sequence': 6}
    for identity, row in sources.items():
        appraisal = appraisals[identity]
        title, url = source_link(row[1])
        if not url.startswith('https://'):
            raise ValueError(f"{identity}: primary source link is missing")
        if appraisal[2][:2] not in directness or appraisal[4] not in horizons:
            raise ValueError(f"{identity}: unknown directness or horizon")
        depth = 'screened-structural' if identity.isdigit() else 'prior-screened-candidate'
        explicit = re.match(r'(selected-full-text|abstract-only):', appraisal[5])
        if explicit:
            depth = explicit[1]
        research.append(dict(id=identity, title=title, url=url,
                             claims=[value.strip() for value in appraisal[6].split(',') if value.strip()],
                             directness=appraisal[2], family=appraisal[3], horizon=appraisal[4],
                             review_depth=depth, record_state='reviewed-catalog' if identity.isdigit() else 'candidate-not-promoted'))
    research = rank(research, lambda row: (claim_priority(row['claims']), directness[row['directness'][:2]], horizons[row['horizon']]))
    landscape = json.loads(texts['repository_source_sha256'])
    repositories = [dict(id=row['id'], repository=row['repository'], url=row['url'], claims=row['claims'],
                         family=row.get('evidence_family', 'unresolved-lineage'), review_depth=row['evidence_depth'],
                         lifecycle=row['lifecycle'], selection_aspect=row.get('selection_aspect', 'not specified'))
                    for row in landscape['repositories']]
    if len({row['id'] for row in repositories}) != len(repositories):
        raise ValueError('duplicate repository IDs')
    repositories = rank(repositories, lambda row: (claim_priority(row['claims']),
                        0 if row['review_depth'] == 'readme-screened' else 1, 0 if row['lifecycle'] == 'current' else 1))
    return dict(schema_version=1, date=as_of, kind='derived appraisal routing projection, not a second findings ledger',
                **{field: hashlib.sha256(text.encode('utf-8')).hexdigest() for field, text in texts.items()},
                rank_meaning='dense priority groups; ties remain ties, stable IDs order display only',
                named_question=QUESTION, ordered_claim_gaps=GAPS,
                rank_dimensions=['named claim gap', 'paper directness then observed horizon OR repository appraisal depth then lifecycle'],
                unmeasured_dimensions={'potential_to_change_conclusion': 'unknown until claim-specific validity review',
                                      'independence': 'families retained; not a rank bonus', 'adoption_readiness': 'not inferred'},
                research=research, repositories=repositories,
                source_hash_encoding='UTF-8 with LF line endings, matching committed Git blob content')


def render(payload):
    papers, repositories = payload['research'], payload['repositories']
    reviewed = sum(row['record_state'] == 'reviewed-catalog' for row in papers)
    screened = sum(row['review_depth'] == 'readme-screened' for row in repositories)
    lines = ['# All-source appraisal priorities', '',
             '**Status:** derived routing projection of the existing ledgers, public-source appraisal routing. It is not a second findings ledger, a scientific confidence score or an adoption recommendation. Assumes Method v2.0 and the named recovery/authority/memory/burden question.', '',
             f'Every one of the {len(papers)} paper records and {len(repositories)} repository records appears once below. The historical {reviewed}-source catalog remains distinct from {len(papers) - reviewed} candidate papers; candidate inclusion here does not promote a finding. Repository coverage includes {screened} README screens and {len(repositories) - screened} portable-only identity records.', '',
             'The [machine-readable projection](staletoast-appraisal-priorities.json) binds hashes of its three source files, using UTF-8 with LF line endings to match committed Git blob content. Rebuild it after any source change. Priority groups order the named claim gaps, then paper directness/horizon or repository review depth/lifecycle. Ties share a dense rank; stable IDs order display only. Stars, citation counts, recency and summed mechanism codes do not decide this priority. Potential to change conclusions is still unknown pending validity review, and family independence is not a rank bonus.', '',
             'The original research evidence-order chart and dated repository popularity orders remain separate views. This projection covers candidates and portable records that those views cannot fairly treat as fully appraised evidence.', '',
             '## Research priorities', '',
             '| Priority group | ID | Source | Review state | Directness / horizon | First gap |',
             '|---|---|---|---|---|---|']
    for row in papers:
        title = row['title'].replace('|', '\\|')
        lines.append(f"| {row['appraisal_priority_rank']} | {row['id']} | [{title}]({row['url']}) | {row['record_state']}; {row['review_depth']} | {row['directness']} / {row['horizon']} | {row['priority_claim']} |")
    lines += ['', '## Repository priorities', '',
              '| Priority group | ID | Repository | Review depth | Lifecycle | First gap |',
              '|---|---|---|---|---|---|']
    for row in repositories:
        lines.append(f"| {row['appraisal_priority_rank']} | {row['id']} | [{row['repository']}]({row['url']}) | {row['review_depth']} | {row['lifecycle']} | {row['priority_claim']} |")
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.write and args.check:
        parser.error('--write and --check are mutually exclusive')
    path = DOCS / 'staletoast-appraisal-priorities.json'
    previous = json.loads(path.read_text(encoding='utf-8')) if path.exists() else None
    as_of = args.date or (previous['date'] if previous else None)
    if not as_of:
        parser.error('--date is required for a new projection')
    payload = build(DOCS, as_of)
    view = DOCS / 'staletoast-appraisal-priorities.md'
    markdown = render(payload)
    if args.check and payload != previous:
        raise ValueError('appraisal projection is stale; rebuild and review it')
    if args.check and (not view.exists() or view.read_text(encoding='utf-8') != markdown):
        raise ValueError('appraisal view is stale; rebuild and review it')
    if args.write:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        view.write_text(markdown, encoding='utf-8')
    print(f"priorities: research={len(payload['research'])} repositories={len(payload['repositories'])}")


if __name__ == '__main__':
    main()
