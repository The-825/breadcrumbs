#!/usr/bin/env python3
"""Portable shared-work checkpoint contract with synthetic self-tests.

This copy-and-adapt tool stores bounded control evidence in an adopter-owned
JSONL file. It does not store prompts, transcripts, provider output, personal
records, credentials, or inferred authority. It performs no network calls,
does not launch providers, and does not push, approve, merge, or deploy.

The caller must supply provider-observed model receipts. A requested or
configured model is not observed evidence. Sessions that do not call this tool
remain uninstrumented and cannot be claimed as checkpointed.

Usage: python3 shared_work_checkpoint.py --selftest
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Union


SCHEMA_VERSION = 1
POLICY_ID = "shared-work-stage-policy-v1"
MAX_EVENTS_PER_SCOPE = 500
MAX_RETRIES = 3
MAX_ITEMS = 24
EVENT_KINDS = frozenset({
    "plan", "decision", "correction", "material_progress", "milestone",
    "blocker", "failure", "workaround", "recovery", "completion",
})
RELEASE_STATES = (
    "working", "committed", "pushed", "pr_open", "checks_pending",
    "checks_failing", "eligible", "approved", "merged",
)
EVIDENCE_STATES = frozenset({"verified", "unknown", "unavailable"})
FRESHNESS_STATES = frozenset({"current", "stale", "unknown"})
USAGE_MEASUREMENTS = frozenset({"measured", "estimated", "unknown"})
_OPAQUE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}")
_COMMIT = re.compile(r"[0-9a-f]{40}")
_DIGEST = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class WorkScope:
    work_id: str
    project_id: str
    repository: str
    worktree: str

    def to_dict(self) -> dict[str, str]:
        return _scope(self)


def stage_policy_contract(stage: str, members: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Validate exact team membership and requested, configured, observed evidence."""
    if stage not in {"planning", "implementation"}:
        raise ValueError("stage must be planning or implementation")
    normalized = [_model_member(member) for member in members]
    principals = [member["principal"] for member in normalized]
    if len(principals) != len(set(principals)):
        raise ValueError("stage team principals must be unique")

    if stage == "planning":
        expected = {
            "jovan": ("owner", None),
            "claude": ("planner", "claude-fable-5-1"),
            "codex": ("reviewer", "gpt-6-astra"),
        }
        if set(principals) != set(expected):
            raise PermissionError(
                "planning requires exactly Jovan, claude-fable-5-1, and gpt-6-astra"
            )
        for member in normalized:
            role, model = expected[member["principal"]]
            if member["role"] != role:
                raise PermissionError(f"{member['principal']} must have role {role}")
            if model:
                _require_exact_model(member, model)
    else:
        if not normalized or "jovan" in principals:
            raise PermissionError("implementation requires one or more agent workers")
        expected = {"claude": "claude-sonnet-5", "codex": "gpt-5.6-sol"}
        for member in normalized:
            model = expected.get(member["principal"])
            if model is None or member["role"] not in {"worker", "subagent"}:
                raise PermissionError("implementation members must be Claude or Codex workers")
            _require_exact_model(member, model)
    return {"policy_id": POLICY_ID, "stage": stage, "members": normalized}


def stage_contracts(
    planning: list[Mapping[str, Any]], implementation: list[Mapping[str, Any]]
) -> dict[str, Any]:
    return {
        "policy_id": POLICY_ID,
        "planning": stage_policy_contract("planning", planning),
        "implementation": stage_policy_contract("implementation", implementation),
    }


def runtime_instrumentation_status(receipt: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    """Report whether a trusted host supplied a usable checkpoint load receipt."""
    if not isinstance(receipt, Mapping):
        return {
            "instrumented": False,
            "claimable": False,
            "reason": "no_trusted_runtime_receipt",
        }
    valid = (
        receipt.get("schema_version") == SCHEMA_VERSION
        and receipt.get("record_type") == "load_receipt"
        and bool(_OPAQUE.fullmatch(str(receipt.get("event_id") or "")))
        and bool(_OPAQUE.fullmatch(str(receipt.get("session_id") or "")))
        and bool(_DIGEST.fullmatch(str(receipt.get("manifest_digest") or "")))
    )
    return {
        "instrumented": valid,
        "claimable": valid,
        "reason": "trusted_runtime_receipt" if valid else "invalid_runtime_receipt",
    }


class WorkCheckpointStore:
    """Append-only scoped checkpoints with idempotent operation IDs.

    JSONL appends flush and fsync. Adopters with concurrent writers must place
    their existing process lock around calls to this class.
    """

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)

    def open(
        self,
        scope: WorkScope,
        *,
        operation_id: str,
        source: str,
        provenance: list[str],
        authority: Mapping[str, Any],
        contracts: Mapping[str, Any],
        plan: Mapping[str, Any],
        remaining: list[str],
        next_action: str,
        evidence: list[str] = (),
        usage: Optional[Mapping[str, Any]] = None,
        occurred_at: Optional[str] = None,
    ) -> dict[str, Any]:
        rows = self._rows(scope)
        if rows and not any(row.get("operation_id") == operation_id for row in rows):
            raise ValueError("work checkpoint scope already exists")
        _authority(authority)
        validated_contracts = _contracts(contracts)
        return self._event(
            scope,
            operation_id=operation_id,
            kind="plan",
            source=source,
            provenance=provenance,
            evidence=evidence,
            remaining=remaining,
            next_action=next_action,
            usage=usage,
            occurred_at=occurred_at,
            authority=dict(authority),
            contracts=validated_contracts,
            plan=_plan(plan),
            plan_revision=1,
            freshness=_freshness(None),
        )

    def revise_plan(
        self,
        scope: WorkScope,
        *,
        operation_id: str,
        source: str,
        provenance: list[str],
        evidence: list[str],
        remaining: list[str],
        next_action: str,
        plan: Mapping[str, Any],
        supersedes_event_id: str,
        freshness: Optional[Mapping[str, Any]] = None,
        usage: Optional[Mapping[str, Any]] = None,
        occurred_at: Optional[str] = None,
    ) -> dict[str, Any]:
        plans = [row for row in self._checkpoints(scope) if row["kind"] == "plan"]
        if not plans or plans[-1]["event_id"] != supersedes_event_id:
            raise ValueError("plan revision must supersede the current plan")
        if plans[-1]["task_state"] == "completed":
            raise ValueError("completed work cannot revise its plan")
        return self._event(
            scope,
            operation_id=operation_id,
            kind="plan",
            source=source,
            provenance=provenance,
            evidence=evidence,
            remaining=remaining,
            next_action=next_action,
            usage=usage,
            occurred_at=occurred_at,
            plan=_plan(plan),
            plan_revision=int(plans[-1]["plan_revision"]) + 1,
            supersedes_event_id=supersedes_event_id,
            freshness=_freshness(freshness),
        )

    def record(
        self,
        scope: WorkScope,
        *,
        operation_id: str,
        kind: str,
        source: str,
        provenance: list[str],
        evidence: list[str],
        remaining: list[str],
        next_action: str,
        freshness: Optional[Mapping[str, Any]] = None,
        usage: Optional[Mapping[str, Any]] = None,
        supersedes_event_id: Optional[str] = None,
        linked_failure_id: Optional[str] = None,
        linked_workaround_id: Optional[str] = None,
        retry_count: Optional[int] = None,
        failure: Optional[Mapping[str, Any]] = None,
        workaround: Optional[Mapping[str, Any]] = None,
        recovery_verified: Optional[bool] = None,
        occurred_at: Optional[str] = None,
    ) -> dict[str, Any]:
        rows = self._checkpoints(scope)
        if not rows:
            raise KeyError("work checkpoint scope is unknown")
        retrying = any(row.get("operation_id") == operation_id for row in rows)
        if rows[-1]["kind"] == "completion" and not retrying:
            raise ValueError("completed work cannot receive another checkpoint")
        if kind not in EVENT_KINDS or kind == "plan":
            raise ValueError("unsupported checkpoint kind")
        by_id = {row["event_id"]: row for row in rows}
        if kind == "correction":
            prior = by_id.get(str(supersedes_event_id))
            if prior is None or prior["kind"] == "completion":
                raise ValueError("correction must supersede a prior nonterminal checkpoint")
        elif supersedes_event_id is not None:
            raise ValueError("only corrections may supersede a checkpoint")
        if kind == "failure":
            failure = _failure(failure)
        elif failure is not None:
            raise ValueError("failure detail belongs only to a failure checkpoint")
        if kind == "workaround":
            linked = by_id.get(str(linked_failure_id))
            if linked is None or linked["kind"] != "failure":
                raise ValueError("workaround must link to a failure in the same scope")
            if retry_count is None or not 1 <= retry_count <= MAX_RETRIES:
                raise ValueError("workaround retry_count is outside the bounded retry policy")
            workaround = _workaround(workaround)
        elif workaround is not None:
            raise ValueError("workaround detail belongs only to a workaround checkpoint")
        if kind == "recovery":
            linked_failure = by_id.get(str(linked_failure_id))
            linked_workaround = by_id.get(str(linked_workaround_id))
            if linked_failure is None or linked_failure["kind"] != "failure":
                raise ValueError("recovery must link to a failure in the same scope")
            if linked_workaround is None or linked_workaround["kind"] != "workaround":
                raise ValueError("recovery must link to a workaround in the same scope")
            if linked_workaround.get("linked_failure_id") != linked_failure_id:
                raise ValueError("recovery links must describe the same retry chain")
            if recovery_verified is not True or not evidence:
                raise ValueError("recovery requires verified evidence")
        if kind in {"failure", "blocker", "workaround"} and not next_action:
            raise ValueError("failure paths require a bounded next action")
        if kind == "completion" and (remaining or next_action or not evidence):
            raise ValueError("completion requires evidence and no remaining work or next action")
        return self._event(
            scope,
            operation_id=operation_id,
            kind=kind,
            source=source,
            provenance=provenance,
            evidence=evidence,
            remaining=remaining,
            next_action=next_action,
            freshness=_freshness(freshness),
            usage=usage,
            occurred_at=occurred_at,
            supersedes_event_id=supersedes_event_id,
            linked_failure_id=linked_failure_id,
            linked_workaround_id=linked_workaround_id,
            retry_count=retry_count,
            failure=failure,
            workaround=workaround,
            recovery_verified=recovery_verified,
        )

    def release(
        self,
        scope: WorkScope,
        *,
        operation_id: str,
        state: str,
        head: Optional[str],
        source: str,
        evidence: list[str],
        pr_ref: Optional[str] = None,
        approval_head: Optional[str] = None,
        merged_head: Optional[str] = None,
        retry_count: int = 0,
        max_retries: int = MAX_RETRIES,
        occurred_at: Optional[str] = None,
    ) -> dict[str, Any]:
        if state not in RELEASE_STATES:
            raise ValueError("unknown release state")
        if not self._checkpoints(scope):
            raise KeyError("work checkpoint scope is unknown")
        existing = next(
            (
                row for row in self._rows(scope)
                if row.get("record_type") == "release"
                and row.get("operation_id") == operation_id
            ),
            None,
        )
        if existing is not None:
            retried = {
                "state": state,
                "head": head,
                "source": source,
                "evidence": list(evidence),
                "pr_ref": pr_ref,
                "approval_head": approval_head,
                "merged_head": merged_head,
                "retry_count": retry_count,
                "max_retries": max_retries,
            }
            if all(existing.get(key) == value for key, value in retried.items()):
                return dict(existing)
            raise ValueError("operation_id already has different release evidence")
        prior = self.release_status(scope)
        if not 0 <= retry_count <= max_retries <= MAX_RETRIES:
            raise ValueError("release retry bounds are invalid")
        if state != "working" and not _is_commit(head):
            raise ValueError("release state requires an exact commit head")
        pr_states = {"pr_open", "checks_pending", "checks_failing", "eligible", "approved", "merged"}
        if state in pr_states and not pr_ref:
            raise ValueError("pull request state requires an exact PR reference")
        if state == "approved":
            if approval_head != head:
                raise PermissionError("approval is not bound to the exact head")
            if prior.get("state") != "eligible" or prior.get("head") != head:
                raise PermissionError("exact-head eligibility is required before approval")
        if state == "merged":
            if merged_head != head:
                raise PermissionError("merge evidence is not bound to the exact head")
            if prior.get("state") != "approved" or prior.get("head") != head:
                raise PermissionError("exact-head approval is required before merge")
        if state == "checks_failing" and (not evidence or retry_count >= max_retries):
            raise RuntimeError("failed checks need evidence and an available bounded retry")

        previous_index = RELEASE_STATES.index(prior["state"]) if prior else -1
        current_index = RELEASE_STATES.index(state)
        new_head = bool(prior and head and head != prior.get("head"))
        retry_restart = bool(
            prior
            and prior.get("state") == "checks_failing"
            and state == "checks_pending"
            and head == prior.get("head")
            and retry_count == int(prior.get("retry_count", 0)) + 1
        )
        if new_head and state != "committed":
            raise PermissionError("a new head must restart release evidence at committed")
        if prior and not new_head and current_index < previous_index and not retry_restart:
            raise ValueError("release state cannot move backward for the same head")

        failure_checkpoint_id = None
        if state == "checks_failing":
            failure_event = self.record(
                scope,
                operation_id=f"{operation_id}:failure",
                kind="failure",
                source=source,
                provenance=[pr_ref or "release"],
                evidence=evidence,
                remaining=["checks_passing"],
                next_action="repair_checks_then_retry",
                failure={
                    "attempted_action": "verify_current_pr_head",
                    "observation": "required_check_failed",
                    "known_cause": "unknown",
                    "suspected_cause": "unknown",
                    "side_effects": "none_observed",
                    "blocker": "required_check_not_passing",
                },
                occurred_at=occurred_at,
            )
            failure_checkpoint_id = failure_event["event_id"]

        record = {
            "schema_version": SCHEMA_VERSION,
            "record_type": "release",
            "operation_id": _id(operation_id, "operation_id"),
            "scope": _scope(scope),
            "state": state,
            "head": head,
            "source": _text(source, "source"),
            "evidence": _items(evidence, "evidence"),
            "pr_ref": _optional(pr_ref, "pr_ref"),
            "approval_head": approval_head,
            "merged_head": merged_head,
            "retry_count": retry_count,
            "max_retries": max_retries,
            "invalidated_prior_head": prior.get("head") if new_head else None,
            "failure_checkpoint_id": failure_checkpoint_id,
            "occurred_at": occurred_at or _now(),
        }
        record["event_id"] = _event_id(record)
        return self._append(record)

    def release_status(self, scope: WorkScope) -> dict[str, Any]:
        releases = [row for row in self._rows(scope) if row.get("record_type") == "release"]
        return dict(releases[-1]) if releases else {}

    def manifest(
        self,
        scope: WorkScope,
        *,
        session_id: str,
        receipt_id: str,
        max_bytes: int = 12_000,
        occurred_at: Optional[str] = None,
    ) -> dict[str, Any]:
        if not 1024 <= max_bytes <= 32_000:
            raise ValueError("manifest byte bound must be from 1024 to 32000")
        checkpoints = self._checkpoints(scope)
        if not checkpoints:
            raise KeyError("work checkpoint scope is unknown")
        superseded = {
            row.get("supersedes_event_id") for row in checkpoints
            if row.get("supersedes_event_id")
        }
        recovered_failures = {
            row.get("linked_failure_id") for row in checkpoints
            if row["kind"] == "recovery" and row.get("recovery_verified")
        }
        recovered_workarounds = {
            row.get("linked_workaround_id") for row in checkpoints
            if row["kind"] == "recovery" and row.get("recovery_verified")
        }
        terminal = checkpoints[-1]["kind"] == "completion"
        active = [] if terminal else [
            _manifest_event(row) for row in checkpoints
            if row["event_id"] not in superseded
            and row["event_id"] not in recovered_failures
            and row["event_id"] not in recovered_workarounds
            and row["kind"] != "milestone"
        ][-MAX_ITEMS:]
        release = self.release_status(scope)
        source_ids = [row["event_id"] for row in checkpoints]
        if release:
            source_ids.append(release["event_id"])
        manifest_digest = _sha256(source_ids)
        receipts = [row for row in self._rows(scope) if row.get("record_type") == "load_receipt"]
        existing_receipt = next(
            (row for row in receipts if row.get("operation_id") == receipt_id), None
        )
        if existing_receipt is not None:
            if (
                existing_receipt.get("manifest_digest") != manifest_digest
                or existing_receipt.get("session_id") != session_id
            ):
                raise ValueError("receipt_id already has different load evidence")
            digest_state = existing_receipt["digest_state"]
        else:
            prior_digest = receipts[-1].get("manifest_digest") if receipts else None
            digest_state = (
                "reused" if prior_digest == manifest_digest
                else "fresh" if prior_digest is None
                else "invalidated"
            )
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "scope": _scope(scope),
            "task_state": "completed" if terminal else "in_progress",
            "active_checkpoints": active,
            "completion": _manifest_event(checkpoints[-1]) if terminal else None,
            "completed_milestones_omitted": sum(
                row["kind"] == "milestone" for row in checkpoints
            ),
            "release": _release_manifest(release),
            "usage": _usage_summary(checkpoints),
            "incremental_digest": manifest_digest,
            "digest_state": digest_state,
            "authority": checkpoints[0]["authority"],
            "contracts": checkpoints[0]["contracts"],
        }
        while len(_canonical(manifest)) > max_bytes and manifest["active_checkpoints"]:
            manifest["active_checkpoints"].pop(0)
        if len(_canonical(manifest)) > max_bytes:
            raise RuntimeError("bounded manifest cannot represent required control state")
        receipt = {
            "schema_version": SCHEMA_VERSION,
            "record_type": "load_receipt",
            "operation_id": _id(receipt_id, "receipt_id"),
            "scope": _scope(scope),
            "session_id": _id(session_id, "session_id"),
            "manifest_digest": manifest_digest,
            "digest_state": digest_state,
            "manifest_bytes": len(_canonical(manifest)),
            "occurred_at": occurred_at or _now(),
        }
        receipt["event_id"] = _event_id(receipt)
        stored = self._append(receipt)
        return {
            **manifest,
            "load_receipt": {
                "schema_version": stored["schema_version"],
                "record_type": stored["record_type"],
                "event_id": stored["event_id"],
                "session_id": stored["session_id"],
                "manifest_digest": stored["manifest_digest"],
                "digest_state": stored["digest_state"],
            },
        }

    def _event(
        self,
        scope: WorkScope,
        *,
        operation_id: str,
        kind: str,
        source: str,
        provenance: list[str],
        evidence: list[str],
        remaining: list[str],
        next_action: str,
        usage: Optional[Mapping[str, Any]],
        occurred_at: Optional[str],
        **extra: Any,
    ) -> dict[str, Any]:
        record = {
            "schema_version": SCHEMA_VERSION,
            "record_type": "checkpoint",
            "operation_id": _id(operation_id, "operation_id"),
            "scope": _scope(scope),
            "kind": kind,
            "task_state": "completed" if kind == "completion" else "in_progress",
            "source": _text(source, "source"),
            "provenance": _items(provenance, "provenance", required=True),
            "evidence": _items(evidence, "evidence"),
            "remaining": _items(remaining, "remaining"),
            "next_action": _text(next_action, "next_action", allow_empty=kind == "completion"),
            "usage": _usage(usage),
            "occurred_at": occurred_at or _now(),
            **{key: value for key, value in extra.items() if value is not None},
        }
        record["event_id"] = _event_id(record)
        return self._append(record)

    def _rows(self, scope: WorkScope) -> list[dict[str, Any]]:
        exact = _scope(scope)
        return [row for row in _read_rows(self.path) if row.get("scope") == exact]

    def _checkpoints(self, scope: WorkScope) -> list[dict[str, Any]]:
        return [row for row in self._rows(scope) if row.get("record_type") == "checkpoint"]

    def _append(self, record: Mapping[str, Any]) -> dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        rows = _read_rows(self.path)
        prior = next(
            (
                row for row in rows
                if row.get("scope") == record.get("scope")
                and row.get("operation_id") == record.get("operation_id")
            ),
            None,
        )
        if prior is not None:
            stable = lambda value: {
                key: item for key, item in value.items()
                if key not in {"event_id", "occurred_at"}
            }
            if stable(prior) != stable(dict(record)):
                raise ValueError("operation_id already has different checkpoint evidence")
            return prior
        if sum(row.get("scope") == record.get("scope") for row in rows) >= MAX_EVENTS_PER_SCOPE:
            raise RuntimeError("work checkpoint event limit reached")
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return dict(record)


def _contracts(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != {"policy_id", "planning", "implementation"}:
        raise ValueError("planning and implementation contracts are required")
    if value.get("policy_id") != POLICY_ID:
        raise PermissionError("unknown shared-work stage policy")
    planning = value.get("planning")
    implementation = value.get("implementation")
    if not isinstance(planning, Mapping) or not isinstance(implementation, Mapping):
        raise ValueError("stage contracts must be objects")
    stage_fields = {"policy_id", "stage", "members"}
    if set(planning) != stage_fields or set(implementation) != stage_fields:
        raise ValueError("stage contract has unknown or missing fields")
    if planning.get("policy_id") != POLICY_ID or implementation.get("policy_id") != POLICY_ID:
        raise PermissionError("unknown nested shared-work stage policy")
    if planning.get("stage") != "planning" or implementation.get("stage") != "implementation":
        raise PermissionError("stage contract is in the wrong lifecycle stage")
    return stage_contracts(
        list(planning.get("members") or []),
        list(implementation.get("members") or []),
    )


def _model_member(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != {"principal", "role", "evidence"}:
        raise ValueError("stage team member has unknown or missing fields")
    principal = _text(value.get("principal"), "principal")
    role = _text(value.get("role"), "role")
    if principal == "jovan":
        if value.get("evidence") is not None:
            raise ValueError("owner model evidence must be null")
        return {"principal": principal, "role": role, "evidence": None}
    evidence = value.get("evidence")
    if not isinstance(evidence, Mapping) or set(evidence) != {"requested", "configured", "observed"}:
        raise PermissionError("requested, configured, and observed model evidence is required")
    normalized = {}
    for name in ("requested", "configured", "observed"):
        item = evidence.get(name)
        if not isinstance(item, Mapping) or set(item) != {"state", "model", "source"}:
            raise PermissionError(f"{name} model evidence is incomplete")
        state = str(item.get("state") or "unknown")
        if state not in EVIDENCE_STATES:
            raise ValueError("unknown model evidence state")
        normalized[name] = {
            "state": state,
            "model": item.get("model"),
            "source": item.get("source"),
        }
    return {"principal": principal, "role": role, "evidence": normalized}


def _require_exact_model(member: Mapping[str, Any], required: str) -> None:
    for evidence_kind in ("requested", "configured", "observed"):
        item = member["evidence"][evidence_kind]
        if (
            item["state"] != "verified"
            or item.get("model") != required
            or not item.get("source")
        ):
            raise PermissionError(
                f"{member['principal']} {evidence_kind} model is unknown, unavailable, or substituted"
            )


def _plan(value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate strict plan structure, not the quality of its prose."""
    required = {
        "objective", "deliverables", "scope", "constraints", "completion_evidence",
        "milestones", "alternatives", "selected_approach", "adversarial",
        "unresolved_issues",
    }
    if not isinstance(value, Mapping) or set(value) != required:
        raise ValueError("saved plan has unknown or missing fields")
    result: dict[str, Any] = {"objective": _text(value["objective"], "objective")}
    for field in ("deliverables", "constraints", "completion_evidence", "milestones"):
        result[field] = _items(value[field], field, required=True)

    scope = value["scope"]
    scope_fields = {"included", "exclusions", "affected_repositories", "dependencies"}
    if not isinstance(scope, Mapping) or set(scope) != scope_fields:
        raise ValueError("plan scope has unknown or missing fields")
    result["scope"] = {
        field: _items(scope[field], f"scope.{field}", required=True)
        for field in sorted(scope_fields)
    }

    alternatives = value["alternatives"]
    if not isinstance(alternatives, list) or not 2 <= len(alternatives) <= 12:
        raise ValueError("plan requires bounded credible alternatives")
    normalized_alternatives = []
    for item in alternatives:
        if not isinstance(item, Mapping) or set(item) != {
            "approach", "tradeoffs", "reuse_or_no_change"
        }:
            raise ValueError("plan alternative has unknown or missing fields")
        normalized_alternatives.append({
            "approach": _text(item["approach"], "alternative.approach"),
            "tradeoffs": _text(item["tradeoffs"], "alternative.tradeoffs"),
            "reuse_or_no_change": item["reuse_or_no_change"] is True,
        })
    if not any(item["reuse_or_no_change"] for item in normalized_alternatives):
        raise ValueError("plan alternatives must include reuse or no-change")
    result["alternatives"] = normalized_alternatives
    result["selected_approach"] = _text(value["selected_approach"], "selected_approach")

    adversarial = value["adversarial"]
    adversarial_fields = {
        "failure_modes", "contradictory_evidence", "edge_cases",
        "privacy_authority", "recovery", "disproof_tests",
    }
    if not isinstance(adversarial, Mapping) or set(adversarial) != adversarial_fields:
        raise ValueError("adversarial plan review has unknown or missing fields")
    result["adversarial"] = {
        field: _items(adversarial[field], f"adversarial.{field}", required=True)
        for field in sorted(adversarial_fields)
    }

    unresolved = value["unresolved_issues"]
    if not isinstance(unresolved, list) or len(unresolved) > 12:
        raise ValueError("unresolved_issues must be a bounded list")
    result["unresolved_issues"] = []
    for item in unresolved:
        if not isinstance(item, Mapping) or set(item) != {"issue", "resolution"}:
            raise ValueError("unresolved issue has unknown or missing fields")
        result["unresolved_issues"].append({
            "issue": _text(item["issue"], "unresolved issue"),
            "resolution": _text(item["resolution"], "unresolved resolution"),
        })
    return result


def _failure(value: Optional[Mapping[str, Any]]) -> dict[str, str]:
    fields = {
        "attempted_action", "observation", "known_cause", "suspected_cause",
        "side_effects", "blocker",
    }
    if not isinstance(value, Mapping) or set(value) != fields:
        raise ValueError("failure detail has unknown or missing fields")
    return {field: _text(value[field], f"failure.{field}") for field in sorted(fields)}


def _workaround(value: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    fields = {"rationale", "checks", "residual_limits"}
    if not isinstance(value, Mapping) or set(value) != fields:
        raise ValueError("workaround detail has unknown or missing fields")
    return {
        "rationale": _text(value["rationale"], "workaround.rationale"),
        "checks": _items(value["checks"], "workaround.checks", required=True),
        "residual_limits": _items(
            value["residual_limits"], "workaround.residual_limits", required=True
        ),
    }


def _freshness(value: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    if value is None:
        return {"state": "unknown", "source_revision": None, "invalidated_by": []}
    if not isinstance(value, Mapping) or set(value) != {
        "state", "source_revision", "invalidated_by"
    }:
        raise ValueError("freshness has unknown or missing fields")
    state = value.get("state")
    if state not in FRESHNESS_STATES:
        raise ValueError("freshness state is invalid")
    revision = value.get("source_revision")
    if state == "current" and not revision:
        raise ValueError("current evidence requires a source revision")
    return {
        "state": state,
        "source_revision": None if revision is None else _text(revision, "source_revision"),
        "invalidated_by": _items(value["invalidated_by"], "invalidated_by"),
    }


def _authority(value: Mapping[str, Any]) -> None:
    if not isinstance(value, Mapping) or set(value) != {"level", "source", "evidence_ref"}:
        raise PermissionError("explicit authority evidence is required")
    if value.get("source") in {None, "", "inferred"}:
        raise PermissionError("authority cannot be inferred")
    for field in ("level", "source", "evidence_ref"):
        _text(value[field], f"authority.{field}")


def _scope(scope: WorkScope) -> dict[str, str]:
    if not isinstance(scope, WorkScope):
        raise ValueError("scope must be a WorkScope")
    return {
        "work_id": _id(scope.work_id, "work_id"),
        "project_id": _id(scope.project_id, "project_id"),
        "repository": _id(scope.repository, "repository"),
        "worktree": _id(scope.worktree, "worktree"),
    }


def _id(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not _OPAQUE.fullmatch(text):
        raise ValueError(f"{field} is not a bounded opaque identifier")
    return text


def _text(value: Any, field: str, *, allow_empty: bool = False) -> str:
    text = str(value or "").strip()
    if (not text and not allow_empty) or len(text) > 512 or "\n" in text or "\r" in text:
        raise ValueError(f"{field} must be bounded single-line text")
    return text


def _optional(value: Any, field: str) -> Optional[str]:
    return None if value is None else _text(value, field)


def _items(values: Any, field: str, *, required: bool = False) -> list[str]:
    if not isinstance(values, (list, tuple)) or len(values) > MAX_ITEMS:
        raise ValueError(f"{field} must be a bounded list")
    result = [_text(value, field) for value in values]
    if required and not result:
        raise ValueError(f"{field} is required")
    return result


def _usage(value: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    value = value or {"measurement": "unknown"}
    fields = {"measurement", "input_tokens", "output_tokens", "cost_usd"}
    unknown = set(value) - fields
    if unknown:
        raise ValueError("usage has unknown fields")
    measurement = str(value.get("measurement") or "unknown")
    if measurement not in USAGE_MEASUREMENTS:
        raise ValueError("usage measurement must be measured, estimated, or unknown")
    result = {
        "measurement": measurement,
        "input_tokens": value.get("input_tokens"),
        "output_tokens": value.get("output_tokens"),
        "cost_usd": value.get("cost_usd"),
    }
    for field in ("input_tokens", "output_tokens"):
        item = result[field]
        if item is not None and (isinstance(item, bool) or not isinstance(item, int) or item < 0):
            raise ValueError(f"usage {field} must be a nonnegative integer")
    cost = result["cost_usd"]
    if cost is not None and (
        isinstance(cost, bool) or not isinstance(cost, (int, float)) or cost < 0
    ):
        raise ValueError("usage cost_usd must be nonnegative")
    if measurement == "unknown" and any(
        result[field] is not None for field in ("input_tokens", "output_tokens", "cost_usd")
    ):
        raise ValueError("unknown usage cannot contain numeric estimates")
    return result


def _usage_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "measured": {"events": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0},
        "estimated": {"events": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0},
        "unknown_events": 0,
    }
    for row in rows:
        usage = row["usage"]
        measurement = usage["measurement"]
        if measurement == "unknown":
            summary["unknown_events"] += 1
            continue
        bucket = summary[measurement]
        bucket["events"] += 1
        for field in ("input_tokens", "output_tokens", "cost_usd"):
            if usage[field] is not None:
                bucket[field] += usage[field]
    return summary


def _manifest_event(row: Mapping[str, Any]) -> dict[str, Any]:
    fields = (
        "event_id", "kind", "source", "provenance", "evidence", "remaining",
        "next_action", "freshness", "plan_revision", "supersedes_event_id",
        "linked_failure_id", "linked_workaround_id", "retry_count", "failure",
        "workaround", "recovery_verified",
    )
    return {field: row[field] for field in fields if field in row}


def _release_manifest(row: Mapping[str, Any]) -> Optional[dict[str, Any]]:
    if not row:
        return None
    fields = (
        "state", "head", "pr_ref", "retry_count", "max_retries",
        "invalidated_prior_head", "evidence", "event_id",
    )
    return {field: row.get(field) for field in fields}


def _read_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed checkpoint row at line {line_number}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"checkpoint row at line {line_number} is not an object")
        rows.append(row)
    return rows


def _is_commit(value: Optional[str]) -> bool:
    return bool(value and _COMMIT.fullmatch(value))


def _event_id(record: Mapping[str, Any]) -> str:
    return "work-" + hashlib.sha256(_canonical(record)).hexdigest()[:24]


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_fixture() -> dict[str, Any]:
    path = Path(__file__).with_name("fixtures") / "shared-work-checkpoint-v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def selftest() -> int:
    checks: list[tuple[str, bool]] = []

    def ok(name: str, result: Any) -> None:
        checks.append((name, bool(result)))

    fixture = _load_fixture()
    contracts = stage_contracts(fixture["planning_members"], fixture["implementation_members"])
    ok("exact planning and implementation teams pass", contracts["policy_id"] == POLICY_ID)
    unknown = json.loads(json.dumps(fixture["implementation_members"]))
    unknown[0]["evidence"]["observed"]["state"] = "unknown"
    try:
        stage_policy_contract("implementation", unknown)
        ok("unknown observed model fails closed", False)
    except PermissionError:
        ok("unknown observed model fails closed", True)
    substituted = json.loads(json.dumps(fixture["planning_members"]))
    substituted[1]["evidence"]["configured"]["model"] = "claude-opus-5"
    try:
        stage_policy_contract("planning", substituted)
        ok("model substitution fails closed", False)
    except PermissionError:
        ok("model substitution fails closed", True)

    uninstrumented = runtime_instrumentation_status(None)
    ok("external session without receipt remains uninstrumented", not uninstrumented["claimable"])

    with tempfile.TemporaryDirectory(prefix="checkpoint_v1_") as temporary:
        store = WorkCheckpointStore(Path(temporary) / "work.jsonl")
        scope = WorkScope(**fixture["scope"])
        opened = store.open(
            scope,
            operation_id="open-1",
            source="operator_request",
            provenance=["task:synthetic-1"],
            evidence=["rules:verified"],
            authority=fixture["authority"],
            contracts=contracts,
            plan=fixture["plan"],
            remaining=["implementation"],
            next_action="implement_fixture",
            occurred_at="2026-01-01T00:00:00+00:00",
        )
        repeated = store.open(
            scope,
            operation_id="open-1",
            source="operator_request",
            provenance=["task:synthetic-1"],
            evidence=["rules:verified"],
            authority=fixture["authority"],
            contracts=contracts,
            plan=fixture["plan"],
            remaining=["implementation"],
            next_action="implement_fixture",
            occurred_at="2026-01-01T00:00:00+00:00",
        )
        ok("operation retry is idempotent", repeated["event_id"] == opened["event_id"])

        invalid_plan = json.loads(json.dumps(fixture["plan"]))
        invalid_plan["unexpected"] = "field"
        try:
            _plan(invalid_plan)
            ok("strict plan rejects unknown fields", False)
        except ValueError:
            ok("strict plan rejects unknown fields", True)

        revised_plan = json.loads(json.dumps(fixture["plan"]))
        revised_plan["objective"] = "Verify the revised synthetic checkpoint contract"
        revised = store.revise_plan(
            scope,
            operation_id="plan-2",
            source="scope_revision",
            provenance=["decision:synthetic-2"],
            evidence=["diff:synthetic"],
            remaining=["conformance"],
            next_action="run_conformance",
            plan=revised_plan,
            supersedes_event_id=opened["event_id"],
            freshness=fixture["freshness"],
            occurred_at="2026-01-01T00:01:00+00:00",
        )
        ok("plan revision increments and supersedes", revised["plan_revision"] == 2)
        try:
            store.revise_plan(
                scope,
                operation_id="plan-stale",
                source="stale_revision",
                provenance=["decision:synthetic-stale"],
                evidence=[],
                remaining=["conformance"],
                next_action="stop",
                plan=revised_plan,
                supersedes_event_id=opened["event_id"],
            )
            ok("stale plan revision is rejected", False)
        except ValueError:
            ok("stale plan revision is rejected", True)

        material = store.record(
            scope,
            operation_id="material-1",
            kind="material_progress",
            source="worker",
            provenance=["commit:synthetic"],
            evidence=["test:focused"],
            remaining=["release"],
            next_action="verify_release",
            freshness=fixture["freshness"],
        )
        store.record(
            scope,
            operation_id="milestone-1",
            kind="milestone",
            source="worker",
            provenance=["test:focused"],
            evidence=["test:passed"],
            remaining=["release"],
            next_action="verify_release",
        )
        decision = store.record(
            scope,
            operation_id="decision-1",
            kind="decision",
            source="owner",
            provenance=["decision:synthetic"],
            evidence=[],
            remaining=["release"],
            next_action="apply_decision",
        )
        correction = store.record(
            scope,
            operation_id="correction-1",
            kind="correction",
            source="owner",
            provenance=["correction:synthetic"],
            evidence=["oracle:synthetic"],
            remaining=["release"],
            next_action="use_correction",
            supersedes_event_id=decision["event_id"],
        )
        failure = store.record(
            scope,
            operation_id="failure-1",
            kind="failure",
            source="ci",
            provenance=["check:synthetic"],
            evidence=["check:failed"],
            remaining=["repair"],
            next_action="apply_bounded_repair",
            failure=fixture["failure"],
        )
        workaround = store.record(
            scope,
            operation_id="workaround-1",
            kind="workaround",
            source="worker",
            provenance=["failure:synthetic"],
            evidence=["patch:synthetic"],
            remaining=["retest"],
            next_action="retest_original_behavior",
            linked_failure_id=failure["event_id"],
            retry_count=1,
            workaround=fixture["workaround"],
        )
        store.record(
            scope,
            operation_id="recovery-1",
            kind="recovery",
            source="ci",
            provenance=["check:synthetic-rerun"],
            evidence=["check:passed"],
            remaining=["release"],
            next_action="continue_release",
            linked_failure_id=failure["event_id"],
            linked_workaround_id=workaround["event_id"],
            recovery_verified=True,
        )
        manifest = WorkCheckpointStore(store.path).manifest(
            scope,
            session_id="restart-1",
            receipt_id="load-1",
            max_bytes=4096,
            occurred_at="2026-01-01T00:02:00+00:00",
        )
        active_ids = {row["event_id"] for row in manifest["active_checkpoints"]}
        ok("restart loads unfinished material progress", material["event_id"] in active_ids)
        ok("correction replaces superseded decision", decision["event_id"] not in active_ids and correction["event_id"] in active_ids)
        ok("completed milestone is omitted", manifest["completed_milestones_omitted"] == 1)
        ok("verified recovery retires retry chain", failure["event_id"] not in active_ids and workaround["event_id"] not in active_ids)
        ok("bounded manifest includes durable receipt", manifest["load_receipt"]["record_type"] == "load_receipt")
        ok("trusted receipt is claimable", runtime_instrumentation_status(manifest["load_receipt"])["claimable"])

        second = store.manifest(scope, session_id="restart-2", receipt_id="load-2", max_bytes=4096)
        ok("unchanged manifest digest is reused", second["digest_state"] == "reused")
        store.record(
            scope,
            operation_id="material-2",
            kind="material_progress",
            source="worker",
            provenance=["commit:synthetic-2"],
            evidence=["test:new"],
            remaining=["release"],
            next_action="refresh_manifest",
        )
        third = store.manifest(scope, session_id="restart-3", receipt_id="load-3", max_bytes=4096)
        ok("new checkpoint invalidates prior digest", third["digest_state"] == "invalidated")

        head_one = "1" * 40
        head_two = "2" * 40
        for operation, state in (
            ("release-1", "committed"),
            ("release-2", "pushed"),
            ("release-3", "pr_open"),
            ("release-4", "eligible"),
        ):
            store.release(
                scope,
                operation_id=operation,
                state=state,
                head=head_one,
                source="git" if state in {"committed", "pushed"} else "forge",
                evidence=[f"state:{state}"],
                pr_ref="pr:synthetic" if state not in {"committed", "pushed"} else None,
            )
        store.release(
            scope,
            operation_id="release-5",
            state="approved",
            head=head_one,
            source="forge",
            evidence=["approval:exact-head"],
            pr_ref="pr:synthetic",
            approval_head=head_one,
        )
        changed = store.release(
            scope,
            operation_id="release-6",
            state="committed",
            head=head_two,
            source="git",
            evidence=["commit:new-head"],
            pr_ref="pr:synthetic",
        )
        ok("new head explicitly invalidates prior head", changed["invalidated_prior_head"] == head_one)
        try:
            store.release(
                scope,
                operation_id="release-stale-merge",
                state="merged",
                head=head_two,
                source="forge",
                evidence=["merge:unverified"],
                pr_ref="pr:synthetic",
                merged_head=head_two,
            )
            ok("merge without exact-head approval is rejected", False)
        except PermissionError:
            ok("merge without exact-head approval is rejected", True)
        for operation, state in (
            ("release-7", "pushed"),
            ("release-8", "pr_open"),
            ("release-9", "eligible"),
        ):
            store.release(
                scope,
                operation_id=operation,
                state=state,
                head=head_two,
                source="git" if state == "pushed" else "forge",
                evidence=[f"state:{state}"],
                pr_ref="pr:synthetic" if state != "pushed" else None,
            )
        store.release(
            scope,
            operation_id="release-10",
            state="approved",
            head=head_two,
            source="forge",
            evidence=["approval:new-head"],
            pr_ref="pr:synthetic",
            approval_head=head_two,
        )
        merged = store.release(
            scope,
            operation_id="release-11",
            state="merged",
            head=head_two,
            source="forge",
            evidence=["merge:new-head"],
            pr_ref="pr:synthetic",
            merged_head=head_two,
        )
        ok("merge verifies the approved exact head", merged["state"] == "merged")

    failed = [name for name, passed in checks if not passed]
    for name, passed in checks:
        print(f"  {'ok  ' if passed else 'FAIL'} {name}")
    print(f"selftest: {len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    return selftest() if args.selftest else 0


if __name__ == "__main__":
    raise SystemExit(main())
