"""Run bounded public reproductions for registered workflow patterns."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "workflow-registry.json"
ROUTING = ROOT / "docs" / "jarvis-workflow-routing.json"
COMMANDS = {
    "WF-001": [sys.executable, "ci-kit/guards/guard_context_budget.py", "--selftest"],
    "WF-002": [sys.executable, "templates/ledger-tools/scoped_context.py", "--selftest"],
    "WF-003": [sys.executable, "-m", "unittest", "discover", "-s", "ci-kit/workflows/tests"],
    "WF-004": [sys.executable, "ci-kit/preflight/preflight.py", "--selftest"],
    "WF-005": [sys.executable, "scripts/workflow_registry.py", "--check"],
}


def reproduce(registry: dict, routing: dict) -> list[str]:
    errors = []
    workflows = {row["id"]: row for row in registry["workflows"]}
    routes = {row["id"]: row for row in routing["routes"]}
    for workflow_id, command in COMMANDS.items():
        workflow = workflows.get(workflow_id)
        if workflow is None:
            errors.append(f"{workflow_id}: registry record is missing")
            continue
        if not workflow.get("jarvis_routes") or any(route not in routes for route in workflow["jarvis_routes"]):
            errors.append(f"{workflow_id}: routable completion contract is missing")
            continue
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if result.returncode:
            errors.append(f"{workflow_id}: reproduction command failed")
            continue
        workflow["adoption_state"] = "reproduced"
        workflow["evidence_level"] = "public-synthetic-reproduction"
        workflow["reproduction"] = {
            "command": " ".join(command[1:]),
            "result": "passed",
            "date": "2026-09-01",
            "claim_boundary": "validates the local pattern contract, not external effectiveness",
        }
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    routing = json.loads(ROUTING.read_text(encoding="utf-8"))
    errors = reproduce(registry, routing)
    if errors:
        print("\n".join(f"workflow_reproduction: {error}" for error in errors))
        return 1
    if args.write:
        REGISTRY.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    elif args.check:
        committed = json.loads(REGISTRY.read_text(encoding="utf-8"))
        if committed != registry:
            print("workflow_reproduction: committed reproduction state is stale")
            return 1
    print("workflow_reproduction: reproduced=5 adopted=0 effectiveness_claims=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
