#!/usr/bin/env python3
"""Deterministic offline replay and review-only memory proposals.

ASSUMES the episodes.jsonl written by the sibling memory_engine.py. This tool
does not call a model, rewrite facts, or activate work. It selects the episodes
that most deserve an offline review, then validates an external evaluator's
output into a typed proposal. Missing or failed evaluation stays ``unknown``.

The "dreaming" analogy means replay during an offline maintenance window. It
does not imply feeling, consciousness, or permission to trust the replay's own
conclusions. Every proposal preserves its source episodes, carries
``mutates: false``, and must pass a later authority gate before durable memory
changes.

Usage:
    python3 governed_replay.py --selftest

As a library:
    episodes = load_episodes(".memory/episodes.jsonl")
    selected = select_replay_episodes(episodes, limit=5)
    proposal = propose_replay(selected, evaluator=my_review_model)
    append_proposal(".memory/replay-proposals.jsonl", proposal)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path


PROPOSAL_TYPES = frozenset(("fact", "skill", "watch", "correction", "unknown"))
HIGH_SIGNAL_ACTIONS = frozenset(("REJECTED", "SUPERSEDED", "PROVENANCE_LINKED"))
HIGH_SIGNAL_TOKENS = frozenset((
    "failure", "failed", "error", "incident", "correction", "tombstone",
    "retrieval-miss", "search-miss", "forbidden-hit",
))


def load_episodes(path):
    """Load valid JSON objects from an append-only episode ledger."""
    rows = []
    for line_no, line in enumerate(
            Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed episode at line {line_no}") from exc
        if not isinstance(row, dict) or not row.get("episode_id"):
            raise ValueError(f"episode at line {line_no} lacks episode_id")
        rows.append(row)
    return rows


def _normalized(text):
    return " ".join(str(text).casefold().split())


def _signal_strength(row):
    action = str(row.get("action", "")).upper()
    tokens = {_normalized(tag).replace("_", "-") for tag in row.get("tags", [])}
    tokens.update(_normalized(action).replace("_", "-").split())
    if action in HIGH_SIGNAL_ACTIONS:
        return 3, "correction-or-lineage event"
    hits = sorted(tokens & HIGH_SIGNAL_TOKENS)
    if hits:
        return 2, "high-consequence tag: " + ", ".join(hits)
    return 0, "ordinary episode"


def select_replay_episodes(episodes, limit=5):
    """Rank episodes deterministically for offline review.

    Priority is structural signal first, repeated outcome second, recency third,
    and the stable episode id last. Recurrence counts exact normalized outcomes;
    semantic similarity belongs in a later, separately evaluated layer.
    """
    if limit < 1:
        raise ValueError("limit must be at least one")
    rows = [dict(row) for row in episodes]
    counts = Counter(_normalized(row.get("outcome", "")) for row in rows)
    ranked = []
    for row in rows:
        signal, signal_reason = _signal_strength(row)
        recurrence = counts[_normalized(row.get("outcome", ""))]
        row["replay_score"] = {
            "signal": signal,
            "recurrence": recurrence,
            "recorded_at": row.get("ts", 0),
        }
        reasons = [signal_reason]
        if recurrence > 1:
            reasons.append(f"exact outcome repeated {recurrence} times")
        row["selection_reasons"] = reasons
        ranked.append(row)
    ranked.sort(key=lambda row: (
        -row["replay_score"]["signal"],
        -row["replay_score"]["recurrence"],
        -row["replay_score"]["recorded_at"],
        str(row["episode_id"]),
    ))
    return ranked[:limit]


def _unknown(selected, reason):
    return {
        "proposal_id": _proposal_id("unknown", "", selected),
        "proposal_type": "unknown",
        "summary": "",
        "reason": reason,
        "source_episode_ids": [row["episode_id"] for row in selected],
        "status": "pending_review",
        "mutates": False,
    }


def _proposal_id(proposal_type, summary, selected):
    seed = json.dumps({
        "proposal_type": proposal_type,
        "summary": _normalized(summary),
        "source_episode_ids": sorted(row["episode_id"] for row in selected),
    }, sort_keys=True, separators=(",", ":"))
    return "replay-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]


def propose_replay(selected, evaluator=None):
    """Validate evaluator output into a stable, non-mutating proposal."""
    selected = [dict(row) for row in selected]
    if not selected:
        return _unknown(selected, "no episodes were selected for replay")
    if evaluator is None:
        return _unknown(selected, "no replay evaluator was supplied")
    try:
        result = evaluator([dict(row) for row in selected])
    except Exception as exc:
        return _unknown(selected, f"replay evaluator failed: {type(exc).__name__}")
    if not isinstance(result, dict):
        return _unknown(selected, "replay evaluator returned a malformed result")
    proposal_type = result.get("proposal_type")
    summary = str(result.get("summary", "")).strip()
    reason = str(result.get("reason", "")).strip()
    chosen = result.get("source_episode_ids")
    selected_ids = {row["episode_id"] for row in selected}
    if proposal_type not in PROPOSAL_TYPES or not reason:
        return _unknown(selected, "replay evaluator returned a malformed result")
    if proposal_type != "unknown" and not summary:
        return _unknown(selected, "a typed replay proposal requires a summary")
    if not isinstance(chosen, list) or not chosen or not set(chosen) <= selected_ids:
        return _unknown(selected, "proposal sources must come from selected episodes")
    return {
        "proposal_id": _proposal_id(proposal_type, summary, [
            row for row in selected if row["episode_id"] in set(chosen)
        ]),
        "proposal_type": proposal_type,
        "summary": summary,
        "reason": reason,
        "source_episode_ids": list(dict.fromkeys(chosen)),
        "status": "pending_review",
        "mutates": False,
    }


def append_proposal(path, proposal):
    """Append once by proposal_id; proposal creation never changes memory."""
    if proposal.get("mutates") is not False \
            or proposal.get("status") != "pending_review" \
            or proposal.get("proposal_type") not in PROPOSAL_TYPES \
            or not proposal.get("proposal_id"):
        raise ValueError(
            "only typed, pending-review, explicitly non-mutating proposals "
            "may enter the replay queue"
        )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing.add(json.loads(line).get("proposal_id"))
    if proposal["proposal_id"] in existing:
        return False
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(proposal, sort_keys=True) + "\n")
    return True


def selftest():
    checks = []

    def ok(name, condition):
        checks.append((name, condition))

    rows = [
        {"episode_id": "ordinary-new", "ts": 30, "action": "CHAT",
         "outcome": "ordinary", "tags": []},
        {"episode_id": "repeat-old", "ts": 10, "action": "OBSERVED",
         "outcome": "same miss", "tags": []},
        {"episode_id": "repeat-new", "ts": 20, "action": "OBSERVED",
         "outcome": "same miss", "tags": []},
        {"episode_id": "correction", "ts": 5, "action": "REJECTED",
         "outcome": "wrong value", "tags": ["tombstone"]},
    ]
    selected = select_replay_episodes(rows, limit=3)
    ok("correction signal outranks mere recency",
       selected[0]["episode_id"] == "correction")
    ok("repeated outcomes outrank ordinary episodes",
       [row["episode_id"] for row in selected[1:]]
       == ["repeat-new", "repeat-old"])
    ok("selection exposes inspectable score and reasons",
       bool(selected[0]["replay_score"]) and selected[0]["selection_reasons"])
    ok("selection is deterministic",
       selected == select_replay_episodes(rows, limit=3))
    try:
        select_replay_episodes(rows, limit=0)
        ok("zero replay budget refused", False)
    except ValueError:
        ok("zero replay budget refused", True)

    missing = propose_replay(selected)
    ok("missing evaluator stays unknown and read-only",
       missing["proposal_type"] == "unknown" and missing["mutates"] is False)
    failed = propose_replay(
        selected, evaluator=lambda _: (_ for _ in ()).throw(RuntimeError("offline"))
    )
    ok("evaluator failure stays unknown", failed["proposal_type"] == "unknown")
    malformed = propose_replay(selected, evaluator=lambda _: {"proposal_type": "fact"})
    ok("malformed evaluator output stays unknown",
       malformed["proposal_type"] == "unknown")
    escaped = propose_replay(selected, evaluator=lambda _: {
        "proposal_type": "fact", "summary": "x", "reason": "r",
        "source_episode_ids": ["not-selected"],
    })
    ok("proposal cannot invent source episodes",
       escaped["proposal_type"] == "unknown")
    proposal = propose_replay(selected, evaluator=lambda chosen: {
        "proposal_type": "correction",
        "summary": "review the rejected value",
        "reason": "a tombstone event deserves explicit follow-up",
        "source_episode_ids": [chosen[0]["episode_id"]],
    })
    ok("typed proposal preserves source and cannot mutate",
       proposal["proposal_type"] == "correction"
       and proposal["source_episode_ids"] == ["correction"]
       and proposal["status"] == "pending_review"
       and proposal["mutates"] is False)
    same = propose_replay(selected, evaluator=lambda chosen: {
        "proposal_type": "correction",
        "summary": "review the rejected value",
        "reason": "same replay",
        "source_episode_ids": [chosen[0]["episode_id"]],
    })
    ok("proposal id is stable across retries",
       proposal["proposal_id"] == same["proposal_id"])
    with tempfile.TemporaryDirectory(prefix="replay_test_") as tmp:
        queue = Path(tmp) / "replay-proposals.jsonl"
        try:
            append_proposal(queue, {**proposal, "mutates": True})
            ok("a mutating proposal is refused at the queue boundary", False)
        except ValueError:
            ok("a mutating proposal is refused at the queue boundary", True)
        ok("first durable proposal append succeeds", append_proposal(queue, proposal))
        ok("retry is idempotent", not append_proposal(queue, proposal))
        saved = json.loads(queue.read_text(encoding="utf-8").strip())
        ok("durable queue preserves the review-only contract",
           saved["mutates"] is False and saved["status"] == "pending_review")

    failed_checks = [name for name, condition in checks if not condition]
    for name, condition in checks:
        print(f"  {'ok  ' if condition else 'FAIL'} {name}")
    print(f"selftest: {len(checks) - len(failed_checks)}/{len(checks)} passed")
    return 1 if failed_checks else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    raise SystemExit(selftest() if args.selftest else 0)
