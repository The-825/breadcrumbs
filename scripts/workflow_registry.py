"""Validate and render the public workflow registry and Jarvis routing projection."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "workflow-registry.json"
ROUTING = ROOT / "docs" / "jarvis-workflow-routing.json"
VIEW = ROOT / "docs" / "workflow-registry.md"


def source_errors(workflow: dict, version: str) -> list[str]:
    identity = workflow.get('id')
    errors = []
    try:
        parsed = urlparse(workflow.get('source_url', ''))
        safe = parsed.scheme == 'https' and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        safe = False
    if not safe:
        return [f'{identity}: a public HTTPS source URL without credentials is required']
    if version == '1.0':
        if parsed.hostname != 'www.reddit.com':
            errors.append(f'{identity}: schema 1.0 requires public Reddit evidence')
        return errors
    source_type = workflow.get('source_type')
    if source_type not in {'community-post', 'repository-documentation', 'official-documentation', 'research-publication'}:
        errors.append(f'{identity}: unsupported primary source type')
    if source_type == 'community-post' and parsed.hostname != 'www.reddit.com':
        errors.append(f'{identity}: community posts retain the Reddit source contract')
    if source_type == 'community-post' and not workflow.get('source_pin'):
        return errors
    pin = workflow.get('source_pin') or {}
    if not isinstance(pin, dict):
        return errors + [f'{identity}: source pin must be an object']
    if not re.fullmatch(r'[0-9a-f]{64}', str(pin.get('content_sha256', ''))):
        errors.append(f'{identity}: source pin needs a SHA-256 content digest')
    if not isinstance(pin.get('version'), str) or not pin['version'].strip():
        errors.append(f'{identity}: source version or commit is required')
    try:
        observed = pin['retrieved_date']
        if date.fromisoformat(observed).isoformat() != observed:
            raise ValueError('noncanonical date')
    except (KeyError, TypeError, ValueError):
        errors.append(f'{identity}: source retrieval date must use YYYY-MM-DD')
    if not isinstance(pin.get('license_status'), str) or not pin['license_status'].strip():
        errors.append(f'{identity}: source license status is required; unknown stays explicit')
    if pin.get('canonical_url') != workflow.get('source_url'):
        errors.append(f'{identity}: pinned canonical URL must match the source URL')
    return errors


def validate(registry: dict, routing: dict) -> list[str]:
    errors = []
    workflows = registry.get("workflows", [])
    routes = routing.get("routes", [])
    workflow_ids = {row.get("id") for row in workflows}
    route_ids = {row.get("id") for row in routes}
    version = registry.get('schema_version')
    if version not in {'1.0', '1.1'} or routing.get("schema_version") != "1.0":
        errors.append("unsupported schema version")
    if len(workflow_ids) != len(workflows) or None in workflow_ids:
        errors.append("workflow IDs are not unique")
    if len(route_ids) != len(routes) or None in route_ids:
        errors.append("route IDs are not unique")
    allowed = set(registry.get("adoption_states", []))
    for workflow in workflows:
        if workflow.get("authority") != "descriptive-only":
            errors.append(f"{workflow.get('id')}: workflow grants authority")
        if workflow.get("adoption_state") not in allowed:
            errors.append(f"{workflow.get('id')}: invalid adoption state")
        errors.extend(source_errors(workflow, version))
        if version == '1.1' and workflow.get('adoption_state') == 'reproduced':
            reproduction = workflow.get('reproduction') or {}
            if not all(reproduction.get(field) for field in ('command', 'date', 'claim_boundary')) or reproduction.get('result') != 'passed':
                errors.append(f"{workflow.get('id')}: reproduced state needs a bounded passing check")
        if version == '1.1' and workflow.get('adoption_state') == 'adopted':
            adoption = workflow.get('adoption') or {}
            if not all(adoption.get(field) for field in ('owner', 'completion_test', 'evidence_url', 'correction_path')):
                errors.append(f"{workflow.get('id')}: adoption needs owner, result evidence and correction path")
        if not workflow.get("limitations") or not workflow.get("validation_signals"):
            errors.append(f"{workflow.get('id')}: evidence boundaries are incomplete")
        if not set(workflow.get("jarvis_routes", [])) <= route_ids:
            errors.append(f"{workflow.get('id')}: unknown Jarvis route")
    for route in routes:
        if not set(route.get("workflow_ids", [])) <= workflow_ids:
            errors.append(f"{route.get('id')}: unknown workflow")
        if not route.get("completion_test"):
            errors.append(f"{route.get('id')}: completion test is required")
    return errors


def render(registry: dict) -> str:
    lines = [
        "# Public workflow registry",
        "",
        registry["evidence_boundary"],
        "",
        "| ID | Workflow | State | Evidence | Jarvis route |",
        "|---|---|---|---|---|",
    ]
    for row in registry["workflows"]:
        lines.append(
            f"| {row['id']} | [{row['title']}]({row['source_url']}) | {row['adoption_state']} | "
            f"{row['evidence_level']} | {', '.join(row['jarvis_routes'])} |"
        )
    lines.extend([
        "", "## Promotion rule", "",
        "A workflow moves from discovered to screened only after its public description and limitations are recorded. Reproduced requires a public or synthetic test. Adopted requires a named owner, measurable completion test, and a correction or withdrawal path. Popularity never substitutes for those checks.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    routing = json.loads(ROUTING.read_text(encoding="utf-8"))
    errors = validate(registry, routing)
    if errors:
        print("\n".join(f"workflow_registry: {error}" for error in errors))
        return 1
    expected = render(registry)
    if args.write:
        VIEW.write_text(expected, encoding="utf-8")
    if args.check and (not VIEW.exists() or VIEW.read_text(encoding="utf-8") != expected):
        print("workflow_registry: generated view is stale")
        return 1
    print(f"workflow_registry: workflows={len(registry['workflows'])} routes={len(routing['routes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
