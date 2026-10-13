"""Build dated editorial charts and a workflow guide from the owning public ledgers.

Standard library only. No network, execution of upstream code, or adoption writes.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from ledger_markdown import source_link

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = ROOT / "site"
HISTORY = DOCS / "staletoast-chart-history"
METHOD = "editorial-routing-v1"


def correct_source_links(edition, records):
    result = copy.deepcopy(edition)
    seen = set()
    for record in records:
        if record['edition_date'] != edition['edition_date']:
            continue
        if record['id'] in seen:
            raise ValueError('duplicate chart source-link correction')
        seen.add(record['id'])
        rows = result['charts']['research']['entries']
        target = next((row for row in rows if row['id'] == record['id']), None)
        if target is None or target['url'] not in {record['original_url'], record['corrected_url']}:
            raise ValueError('chart correction does not match its source record')
        if record['ledger_sha256'] != edition.get('source_hashes', {}).get('research_source_sha256'):
            raise ValueError('chart correction is not bound to the frozen source ledger')
        title, url = source_link(record['source_excerpt'])
        if title != target['title'] or url != record['corrected_url']:
            raise ValueError('chart correction differs from its cited source excerpt')
        if date.fromisoformat(record['recorded_date']).isoformat() != record['recorded_date']:
            raise ValueError('chart correction date must use YYYY-MM-DD')
        target['url'] = public_url(url)
        target['source_link_correction'] = dict(recorded_date=record['recorded_date'],
                                               reason=record['reason'], original_url=record['original_url'],
                                               evidence_url=public_url(record['evidence_url']))
    return result


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def public_url(value):
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("a public HTTPS source URL is required")
    return value


def editions(history=None):
    history = history or HISTORY
    result = []
    for path in sorted(history.glob("*.json")):
        record = read(path)
        if date.fromisoformat(record["edition_date"]).isoformat() != record["edition_date"]:
            raise ValueError("chart dates must use YYYY-MM-DD")
        if path.stem != record["edition_date"] or record.get("method_version") != METHOD:
            raise ValueError("chart history identity or method mismatch")
        for kind in ("research", "repositories"):
            rows = record["charts"][kind]["entries"]
            if len(rows) > 100 or len({r["id"] for r in rows}) != len(rows):
                raise ValueError("chart history has duplicate IDs or exceeds 100")
            if [r["position"] for r in rows] != list(range(1, len(rows) + 1)):
                raise ValueError("chart positions are not contiguous")
        result.append(record)
    return result


def make_edition(edition_date, priorities, landscape, prior_editions):
    if date.fromisoformat(edition_date).isoformat() != edition_date:
        raise ValueError("chart dates must use YYYY-MM-DD")
    if prior_editions and edition_date <= prior_editions[-1]["edition_date"]:
        raise ValueError("new chart editions must follow the latest frozen date")
    repositories = {row["id"]: row for row in landscape["repositories"]}
    if len(repositories) != len(landscape["repositories"]):
        raise ValueError("duplicate source repository IDs")
    for kind in ("research", "repositories"):
        ids = [row["id"] for row in priorities[kind]]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate priority IDs")
    if {row["id"] for row in priorities["repositories"]} != set(repositories):
        raise ValueError("repository priorities do not cover the ledger")
    result = dict(schema_version=1, edition_date=edition_date, method_version=METHOD,
                  question=priorities["named_question"], charts={})
    for kind in ("research", "repositories"):
        eligible = [row for row in priorities[kind]
                    if kind == "research" or row["review_depth"] == "readme-screened"]
        # Tied priority groups remain visible; position is a display order, not a score.
        eligible.sort(key=lambda row: (row["priority_key"], row["id"]))
        last = {row["id"]: row for row in prior_editions[-1]["charts"][kind]["entries"]} if prior_editions else {}
        entries = []
        for position, row in enumerate(eligible[:100], 1):
            old = last.get(row["id"])
            appearances = [entry for edition in prior_editions
                           for entry in edition["charts"][kind]["entries"] if entry["id"] == row["id"]]
            entry = dict(id=row["id"], position=position, title=row.get("title", row.get("repository")),
                         url=public_url(row["url"]), claims=row["claims"], family=row["family"],
                         priority_group=row["appraisal_priority_rank"], reason=f"Relevant to {row['priority_claim']}; {row['review_depth']} evidence",
                         evidence_depth=row["review_depth"], previous_position=old["position"] if old else None,
                         movement=old["position"] - position if old else None,
                         entry_state="continuing" if old else ("reentry" if appearances else "new"),
                         peak_position=min([position] + [entry["position"] for entry in appearances]),
                         appearances=len(appearances) + 1)
            if kind == "research":
                entry.update(record_state=row["record_state"], directness=row["directness"], horizon=row["horizon"])
            else:
                source = repositories[row["id"]]
                entry.update(snapshot_commit=source["snapshot_commit"], reviewed_date=source["snapshot_date"],
                             category=source["category"], license_status=source["license_status"],
                             stars_observed=source["stars_observed"], stars_observed_date=source.get("popularity_observed_date", source.get("stars_observed_date", landscape["popularity_observed_date"])))
            entries.append(entry)
        cutoff = eligible[99]["appraisal_priority_rank"] if len(eligible) >= 100 else None
        result["charts"][kind] = dict(eligible_count=len(eligible), archive_count=len(priorities[kind]), entries=entries,
                                      cutoff_tied_outside_chart=sum(row["appraisal_priority_rank"] == cutoff for row in eligible[100:]) if cutoff else 0,
                                      off_chart_ids=[row["id"] for row in eligible[100:]])
    return result


def freeze(path, edition):
    if path.exists():
        if read(path) != edition:
            raise ValueError("a frozen chart edition cannot be overwritten")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(edition, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def workflow_catalog(registry):
    output = []
    for row in registry["workflows"]:
        guide = row.get("guide")
        if not guide:
            continue
        if row["authority"] != "descriptive-only":
            raise ValueError("workflow publication cannot grant authority")
        for field in ("when_to_use", "when_to_skip", "requirements", "steps", "example", "completion_check", "failure_modes"):
            if not guide.get(field):
                raise ValueError(f"{row['id']}: incomplete workflow article ({field})")
        if len(guide["steps"]) < 2:
            raise ValueError("workflow articles need an actionable sequence")
        for artifact in guide.get("artifacts", []):
            public_url(artifact["url"])
        output.append(dict(id=row["id"], title=row["title"], categories=row["categories"], problem=row["problem"],
                           pattern=row["pattern"], source_url=public_url(row["source_url"]), evidence_level=row["evidence_level"],
                           adoption_state=row["adoption_state"], limitations=row["limitations"],
                           reproduction=row.get("reproduction"), guide=guide, authority="descriptive-only"))
    if len({row["id"] for row in output}) != len(output):
        raise ValueError("duplicate workflow article ID")
    return output


def prompt_catalog(catalog):
    if catalog.get('schema_version') != '1.0':
        raise ValueError('unsupported prompt catalog version')
    rows = catalog['prompts']
    if len({row['id'] for row in rows}) != len(rows):
        raise ValueError('duplicate prompt IDs')
    for row in rows:
        for field in ('title', 'purpose', 'template', 'version'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError('prompt description or template is incomplete')
        if date.fromisoformat(row['reviewed_date']).isoformat() != row['reviewed_date']:
            raise ValueError('prompt review date must use YYYY-MM-DD')
        if row['category'] not in {'workflows', 'data-stacks', 'systems'}:
            raise ValueError('unknown prompt category')
        if row['authority'] != 'descriptive-only' or row['model_evaluation'] != 'not-run':
            raise ValueError('prompt authority or evaluation needs a reviewed contract change')
        fields = row['required_inputs']
        placeholders = set(re.findall(r'\{\{([A-Z_]+)\}\}', row['template']))
        if not fields or len(set(fields)) != len(fields) or placeholders != set(fields) or set(row['sample_inputs']) != set(fields):
            raise ValueError('prompt input and example fields do not match')
        if not all(isinstance(value, str) and value.strip() for value in row['sample_inputs'].values()):
            raise ValueError('prompt examples need explicit text inputs')
        if not row['output_checks'] or not row['limitations'] or not row['source_urls']:
            raise ValueError('prompt evidence boundaries are incomplete')
        for url in row['source_urls']:
            public_url(url)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--edition-date")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if DOCS == ROOT / "docs" and (ROOT / "staletoast-consumer.json").exists():
        if args.edition_date:
            parser.error("Chart editions are owned by The-825/staletoast")
        from catalog_consumer import load_export
        charts = load_export()["catalogs"]["charts"]
        workflows = workflow_catalog(read(DOCS / "workflow-registry.json"))
        prompts = prompt_catalog(read(DOCS / "prompt-library.json"))
        for name, payload in (("charts.json", charts), ("workflows.json", workflows), ("prompts.json", prompts)):
            path = SITE / "data" / name
            text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
            if args.check:
                if not path.exists() or path.read_text(encoding="utf-8") != text:
                    raise ValueError("generated " + name + " is stale")
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
        print("discovery: StaleToast consumer; workflows=" + str(len(workflows)) + " prompts=" + str(len(prompts)))
        return
    previous = editions()
    correction_path = DOCS / 'staletoast-chart-link-corrections.json'
    correction_catalog = read(correction_path) if correction_path.exists() else {'schema_version': '1.0', 'records': []}
    if correction_catalog.get('schema_version') != '1.0':
        raise ValueError('unsupported chart source-link correction version')
    corrections = correction_catalog['records']
    if args.edition_date:
        priorities = read(DOCS / "staletoast-appraisal-priorities.json")
        sources = {"research_source_sha256": "collaborative-intelligence-research-ledger.md",
                   "appraisal_source_sha256": "collaborative-intelligence-source-appraisals.md",
                   "repository_source_sha256": "collaborative-intelligence-repository-landscape.json"}
        if any(priorities[field] != digest(DOCS / name) for field, name in sources.items()):
            raise ValueError("appraisal priorities are stale; rebuild before freezing an edition")
        earlier = [record for record in previous if record["edition_date"] < args.edition_date]
        edition = make_edition(args.edition_date, priorities, read(DOCS / "collaborative-intelligence-repository-landscape.json"), earlier)
        edition["source_hashes"] = {field: priorities[field] for field in sources}
        path = HISTORY / f"{args.edition_date}.json"
        if args.check:
            if not path.exists() or correct_source_links(read(path), corrections) != correct_source_links(edition, corrections):
                raise ValueError("frozen edition is missing or differs; check mode does not write")
        else:
            if path.exists():
                if correct_source_links(read(path), corrections) != correct_source_links(edition, corrections):
                    raise ValueError('a frozen chart edition cannot be overwritten')
            else:
                freeze(path, edition)
        previous = editions()
    if not previous:
        raise ValueError("no frozen chart edition; supply --edition-date")
    for record in corrections:
        if record['edition_date'] not in {edition['edition_date'] for edition in previous}:
            raise ValueError('correction targets an unknown chart edition')
    previous = [correct_source_links(edition, corrections) for edition in previous]
    charts = dict(latest=previous[-1], history=[dict(edition_date=row["edition_date"], method_version=row["method_version"], charts=row["charts"]) for row in previous])
    workflows = workflow_catalog(read(DOCS / "workflow-registry.json"))
    prompts = prompt_catalog(read(DOCS / 'prompt-library.json'))
    for name, payload in (("charts.json", charts), ("workflows.json", workflows), ("prompts.json", prompts)):
        path = SITE / "data" / name
        text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                raise ValueError(f"generated {name} is stale")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    print(f"discovery: research={len(charts['latest']['charts']['research']['entries'])} repositories={len(charts['latest']['charts']['repositories']['entries'])} workflows={len(workflows)} prompts={len(prompts)} editions={len(previous)}")


if __name__ == "__main__":
    main()
