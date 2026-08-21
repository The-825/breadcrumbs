#!/usr/bin/env python3
"""Append-only learning cycles with evidence-gated mastery.

This public tool uses generic pedagogy terms. It records a sourced lesson,
applications or teach-backs, externally evaluated understanding, transfer to a
novel context, and a final mastery proposal. Nothing here rewrites memory or
activates a skill.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


AUTHORITIES = frozenset(("tool", "human"))
VERDICTS = frozenset(("passed", "failed", "unknown"))


def _stable_id(prefix, payload):
    seed = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return prefix + "-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]


def start_cycle(objective, knowledge, source_ids):
    """Create a source-linked learning cycle; knowledge is not mastery."""
    objective = str(objective).strip()
    knowledge = str(knowledge).strip()
    sources = list(dict.fromkeys(source_ids)) if isinstance(source_ids, list) else []
    if not objective or not knowledge or not sources or not all(sources):
        raise ValueError("objective, knowledge, and at least one source are required")
    core = {"objective": objective, "knowledge": knowledge, "source_ids": sources}
    return {
        "cycle_id": _stable_id("learn", core), **core,
        "events": [{"stage": "knowledge", "source_ids": sources}],
        "learning_status": "knowledge",
        "mastery": False,
        "mutates_memory": False,
    }


def record_application(cycle, mode, artifact_id, summary):
    """Record wisdom as application or teach-back, without claiming success."""
    if mode not in ("application", "teach_back"):
        raise ValueError("mode must be application or teach_back")
    if not str(artifact_id).strip() or not str(summary).strip():
        raise ValueError("application evidence requires an artifact and summary")
    out = json.loads(json.dumps(cycle))
    out["events"].append({
        "stage": "wisdom", "mode": mode, "artifact_id": str(artifact_id),
        "summary": str(summary).strip(),
    })
    out["learning_status"] = "wisdom"
    return out


def evaluate_attempt(cycle, artifact_id, expected, observed, verifier):
    """Record understanding evidence; failed evaluation never disappears."""
    if verifier.get("authority") not in AUTHORITIES or not verifier.get("actor"):
        raise ValueError("evaluation requires a named tool or human verifier")
    verdict = verifier.get("verdict", "unknown")
    if verdict not in VERDICTS:
        verdict = "unknown"
    expected = list(expected) if isinstance(expected, list) else []
    observed = list(observed) if isinstance(observed, list) else []
    if not expected or not all(isinstance(x, str) for x in expected + observed):
        verdict = "unknown"
    if verdict == "passed" and not set(expected) <= set(observed):
        verdict = "failed"
    out = json.loads(json.dumps(cycle))
    out["events"].append({
        "stage": "understanding", "artifact_id": str(artifact_id),
        "expected": expected, "observed": observed, "verdict": verdict,
        "verifier": {"actor": verifier.get("actor"),
                     "authority": verifier.get("authority")},
        "reason": str(verifier.get("reason", "")).strip(),
    })
    out["learning_status"] = "understanding" if verdict == "passed" else verdict
    return out


def record_transfer(cycle, context_id, artifact_id, verifier):
    """Record performance in a distinct context as transfer evidence."""
    known_contexts = {event.get("context_id") for event in cycle["events"]
                      if event.get("stage") == "transfer"}
    if not context_id or context_id in known_contexts:
        raise ValueError("transfer requires a new, distinct context")
    if verifier.get("authority") not in AUTHORITIES or not verifier.get("actor"):
        raise ValueError("transfer requires a named tool or human verifier")
    verdict = verifier.get("verdict", "unknown")
    if verdict not in VERDICTS:
        verdict = "unknown"
    out = json.loads(json.dumps(cycle))
    out["events"].append({
        "stage": "transfer", "context_id": str(context_id),
        "artifact_id": str(artifact_id), "verdict": verdict,
        "verifier": {"actor": verifier.get("actor"),
                     "authority": verifier.get("authority")},
        "reason": str(verifier.get("reason", "")).strip(),
    })
    out["learning_status"] = "transfer" if verdict == "passed" else verdict
    return out


def propose_mastery(cycle, min_understanding=1, min_transfer=1):
    """Propose a capability as born only after understanding and transfer pass."""
    understanding = [e for e in cycle["events"]
                     if e.get("stage") == "understanding" and e.get("verdict") == "passed"]
    transfer = [e for e in cycle["events"]
                if e.get("stage") == "transfer" and e.get("verdict") == "passed"]
    eligible = len(understanding) >= min_understanding and len(transfer) >= min_transfer
    out = json.loads(json.dumps(cycle))
    out["mastery_proposal"] = {
        "proposal_id": _stable_id("mastery", {
            "cycle_id": cycle["cycle_id"],
            "understanding": [e["artifact_id"] for e in understanding],
            "transfer": [e["artifact_id"] for e in transfer],
        }),
        "status": "pending_review" if eligible else "insufficient_evidence",
        "eligible": eligible,
        "understanding_count": len(understanding),
        "transfer_count": len(transfer),
        "mutates_memory": False,
    }
    out["learning_status"] = "born_proposed" if eligible else out["learning_status"]
    out["mastery"] = False
    return out


def append_cycle(path, cycle):
    """Append the complete cipher once by its stable current snapshot id."""
    snapshot = {"cycle_id": cycle["cycle_id"], "events": cycle["events"],
                "mastery_proposal": cycle.get("mastery_proposal")}
    row = {**cycle, "snapshot_id": _stable_id("cipher", snapshot)}
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = set()
    if path.exists():
        existing = {json.loads(line)["snapshot_id"] for line in
                    path.read_text(encoding="utf-8").splitlines() if line.strip()}
    if row["snapshot_id"] in existing:
        return False
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
    return True


def selftest():
    checks = []
    def ok(name, value): checks.append((name, bool(value)))
    cycle = start_cycle("apply provenance", "claims cite sources", ["source-1"])
    ok("knowledge begins sourced and not mastered", cycle["source_ids"] and not cycle["mastery"])
    ok("learning never mutates memory", cycle["mutates_memory"] is False)
    same = start_cycle("apply provenance", "claims cite sources", ["source-1"])
    ok("cycle id is stable", cycle["cycle_id"] == same["cycle_id"])
    try:
        start_cycle("x", "y", [])
        ok("unsourced knowledge refused", False)
    except ValueError: ok("unsourced knowledge refused", True)
    cycle = record_application(cycle, "teach_back", "teach-1", "explain the source trail")
    ok("teach-back records wisdom without mastery", cycle["learning_status"] == "wisdom" and not cycle["mastery"])
    failed = evaluate_attempt(cycle, "teach-1", ["source named"], [],
                              {"actor":"exam", "authority":"tool", "verdict":"passed"})
    ok("missing expected outcome forces failure", failed["events"][-1]["verdict"] == "failed")
    cycle = evaluate_attempt(cycle, "teach-1", ["source named"], ["source named"],
                             {"actor":"exam", "authority":"tool", "verdict":"passed"})
    ok("external evidence can establish understanding", cycle["learning_status"] == "understanding")
    try:
        evaluate_attempt(cycle, "teach-1", ["x"], ["x"],
                         {"actor":"agent", "authority":"agent", "verdict":"passed"})
        ok("agent self-evaluation refused", False)
    except ValueError: ok("agent self-evaluation refused", True)
    premature = propose_mastery(cycle)
    ok("understanding alone cannot propose mastery", not premature["mastery_proposal"]["eligible"])
    cycle = record_transfer(cycle, "novel-context", "transfer-1",
                            {"actor":"operator", "authority":"human", "verdict":"passed"})
    ok("novel-context success records transfer", cycle["learning_status"] == "transfer")
    try:
        record_transfer(cycle, "novel-context", "transfer-2",
                        {"actor":"operator", "authority":"human", "verdict":"passed"})
        ok("duplicate transfer context refused", False)
    except ValueError: ok("duplicate transfer context refused", True)
    proposed = propose_mastery(cycle)
    ok("understanding plus transfer can propose born", proposed["learning_status"] == "born_proposed")
    ok("born remains review-only and non-mutating",
       proposed["mastery_proposal"]["status"] == "pending_review"
       and proposed["mastery_proposal"]["mutates_memory"] is False
       and proposed["mastery"] is False)
    retry = propose_mastery(cycle)
    ok("mastery proposal id is stable", proposed["mastery_proposal"]["proposal_id"] == retry["mastery_proposal"]["proposal_id"])
    with tempfile.TemporaryDirectory(prefix="learning_test_") as tmp:
        ledger = Path(tmp) / "learning-cycles.jsonl"
        ok("first cipher snapshot appends", append_cycle(ledger, proposed))
        ok("cipher retry is idempotent", not append_cycle(ledger, proposed))
        saved = json.loads(ledger.read_text(encoding="utf-8").strip())
        ok("cipher preserves the entire learning trail", len(saved["events"]) == 4)
    failures = [name for name, value in checks if not value]
    for name, value in checks: print(f"  {'ok  ' if value else 'FAIL'} {name}")
    print(f"selftest: {len(checks)-len(failures)}/{len(checks)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    raise SystemExit(selftest() if args.selftest else 0)
