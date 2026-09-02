"""Validate and render the public workflow registry and Jarvis routing projection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "workflow-registry.json"
ROUTING = ROOT / "docs" / "jarvis-workflow-routing.json"
VIEW = ROOT / "docs" / "workflow-registry.md"


def validate(registry: dict, routing: dict) -> list[str]:
    errors = []
    workflows = registry.get("workflows", [])
    routes = routing.get("routes", [])
    workflow_ids = {row.get("id") for row in workflows}
    route_ids = {row.get("id") for row in routes}
    if registry.get("schema_version") != "1.0" or routing.get("schema_version") != "1.0":
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
        if not workflow.get("source_url", "").startswith("https://www.reddit.com/"):
            errors.append(f"{workflow.get('id')}: source is not public Reddit evidence")
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
