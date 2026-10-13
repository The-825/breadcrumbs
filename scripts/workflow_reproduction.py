"""Run bounded public reproductions for registered workflow patterns."""

from __future__ import annotations

import argparse
import copy
from datetime import date, datetime, timezone
import json
import re
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


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def evidence_date(value: object, run_date: date) -> str | None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
        return "missing or malformed evidence date"
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return "missing or malformed evidence date"
    if parsed > run_date:
        return "future evidence date"
    return None


def reproduce(registry: dict, routing: dict, *, run_date: date, check: bool = False,
              runner=subprocess.run) -> list[str]:
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
        recorded_date = run_date.isoformat()
        if check:
            reproduction = workflow.get("reproduction")
            historical_date = reproduction.get("date") if isinstance(reproduction, dict) else None
            reason = evidence_date(historical_date, run_date)
            if reason:
                errors.append(f"{workflow_id}: {reason}")
            else:
                recorded_date = historical_date
        result = runner(command, cwd=ROOT, text=True, capture_output=True)
        if result.returncode:
            errors.append(f"{workflow_id}: reproduction command failed")
            continue
        workflow["adoption_state"] = "reproduced"
        workflow["evidence_level"] = "public-synthetic-reproduction"
        workflow["reproduction"] = {
            "command": " ".join(command[1:]),
            "result": "passed",
            "date": recorded_date,
            "claim_boundary": "validates the local pattern contract, not external effectiveness",
        }
    return errors


def main(argv=None, *, registry_path=REGISTRY, routing_path=ROUTING,
         runner=subprocess.run, clock=utc_now) -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--write", action="store_true")
    modes.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    instant = clock()
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("workflow_reproduction clock must return an aware datetime")
    run_date = instant.astimezone(timezone.utc).date()
    registry_path = Path(registry_path)
    committed = json.loads(registry_path.read_text(encoding="utf-8"))
    registry = copy.deepcopy(committed)
    routing = json.loads(Path(routing_path).read_text(encoding="utf-8"))
    errors = reproduce(registry, routing, run_date=run_date, check=args.check, runner=runner)
    if args.check and committed != registry:
        errors.append("committed reproduction state is stale")
    if errors:
        print("\n".join(f"workflow_reproduction: {error}" for error in errors))
        return 1
    if args.write:
        registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8", newline="\n")
    reproduced = sum(row["id"] in COMMANDS for row in registry["workflows"])
    print(f"workflow_reproduction: reproduced={reproduced} adopted=0 effectiveness_claims=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
