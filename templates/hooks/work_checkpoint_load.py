#!/usr/bin/env python3
"""SessionStart hook for an adopter-owned shared-work checkpoint ledger.

Register this hook only on a trusted lifecycle event. The harness supplies a
``work_checkpoint`` object with ``ledger_path``, ``scope``, ``receipt_id``, and
optional ``max_bytes`` plus a top-level ``session_id``. Missing configuration
reports uninstrumented state. Invalid or unavailable state reports unknown.
Neither case is converted into a successful load receipt.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping


def _contract_module():
    path = Path(__file__).resolve().parent.parent / "ledger-tools" / "shared_work_checkpoint.py"
    spec = importlib.util.spec_from_file_location("shared_work_checkpoint", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("checkpoint contract is unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    contract = payload.get("work_checkpoint") if isinstance(payload, Mapping) else None
    if not isinstance(contract, Mapping):
        return {
            "status": "uninstrumented",
            "claimable": False,
            "reason": "trusted_work_checkpoint_payload_missing",
        }
    required = {"ledger_path", "scope", "receipt_id"}
    if not required.issubset(contract) or not payload.get("session_id"):
        return {
            "status": "uninstrumented",
            "claimable": False,
            "reason": "trusted_work_checkpoint_fields_missing",
        }
    module = _contract_module()
    try:
        scope = module.WorkScope(**contract["scope"])
        manifest = module.WorkCheckpointStore(contract["ledger_path"]).manifest(
            scope,
            session_id=payload["session_id"],
            receipt_id=contract["receipt_id"],
            max_bytes=contract.get("max_bytes", 12_000),
        )
    except (KeyError, OSError, TypeError, ValueError, RuntimeError) as exc:
        return {
            "status": "unknown",
            "claimable": False,
            "reason": type(exc).__name__,
        }
    return {"status": "loaded", "claimable": True, "manifest": manifest}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        payload = {}
    result = load_from_payload(payload)
    print(json.dumps({"systemMessage": json.dumps(result, sort_keys=True)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
