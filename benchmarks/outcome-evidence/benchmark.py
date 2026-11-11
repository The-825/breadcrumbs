#!/usr/bin/env python3
"""Experimental synthetic outcome-evidence check. Not production enforcement.

Compares what a run claimed with what a separately supplied synthetic
observation registry supports. Observer trust is a caller-supplied fixture
assumption, not authentication of a real observer. Standard library only, no
network, no model calls. Python 3.9+.

The audit decision never sees expectations. Expectations are read only after
the audit, to verify the fixture. The shipped checkpoint store is imported and
called as a baseline; its acceptance is a recording behavior, not a verdict.

Usage:
    python3 benchmark.py             JSON report on stdout
    python3 benchmark.py --selftest  run test_benchmark.py
Exit codes: 0 verified, 1 fixture expectations not met, 2 malformed input.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Optional

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CASES_PATH = HERE / "cases.json"
OBSERVATIONS_PATH = HERE / "observations.json"
EXPECTED_PATH = HERE / "expected.json"
CHECKPOINT_PATH = ROOT / "templates" / "ledger-tools" / "shared_work_checkpoint.py"
CHECKPOINT_FIXTURE_PATH = ROOT / "templates" / "ledger-tools" / "fixtures" / "shared-work-checkpoint-v1.json"
CHECKPOINT_LABEL = "templates/ledger-tools/shared_work_checkpoint.py"
CHECKPOINT_FIXTURE_LABEL = "templates/ledger-tools/fixtures/shared-work-checkpoint-v1.json"

NOTICE = (
    "Experimental synthetic evidence checking. Observation trust is a "
    "caller-supplied fixture assumption, not observer authentication, and "
    "nothing here is production enforcement or a measure of real task success."
)
BASELINE_NOTE = (
    "baseline recording is whether the shipped checkpoint store accepted a "
    "completion record with the case's evidence text. It is not an outcome "
    "verdict and not a finding about that store."
)
FIXED_TIME = "2026-01-01T00:00:00+00:00"

OUTCOMES = ("passed", "failed", "unknown")
PROOF_CATEGORIES = frozenset({"environment_state", "artifact", "action_result"})
NONPROOF_CATEGORIES = frozenset({
    "statement", "agent_memory", "tool_call", "final_answer",
})
ALL_CATEGORIES = PROOF_CATEGORIES | NONPROOF_CATEGORIES
VALUE_TYPES = frozenset({"bool", "int", "string", "null"})
CORRECTION_CODES = frozenset({"format_mismatch", "strict_string_mismatch"})
CORRECTION_STATUSES = ("none", "authorized", "rejected")
BASELINE_STATUSES = ("accepted", "rejected")
MAX_CASES = 64
MAX_OBSERVATIONS = 256
MAX_REQUIREMENTS = 8

_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,63}")


class FixtureError(ValueError):
    """Malformed or inconsistent input. Evidence is never silently dropped."""


# ---------------------------------------------------------------- loading

def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise FixtureError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def _no_constant(name):
    raise FixtureError(f"non-finite JSON constant: {name}")


def parse_json(data: bytes, label: str) -> Any:
    try:
        return json.loads(
            data.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_no_constant
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise FixtureError(f"{label} is not valid JSON: {type(exc).__name__}") from exc


def _read(path: Path, label: str) -> bytes:
    try:
        return Path(path).read_bytes()
    except OSError as exc:
        raise FixtureError(f"cannot read {label}: {type(exc).__name__}") from exc


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ------------------------------------------------------------- validation

def _id(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise FixtureError(f"{field} is not a valid identifier")
    return value


def _exact(obj: Any, required, optional, field: str) -> None:
    if not isinstance(obj, dict):
        raise FixtureError(f"{field} must be an object")
    missing = sorted(set(required) - set(obj))
    extra = sorted(set(obj) - set(required) - set(optional))
    if missing or extra:
        raise FixtureError(f"{field} fields invalid: missing {missing}, unknown {extra}")


def _enum(value: Any, allowed, field: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise FixtureError(f"{field} is not an allowed value")
    return value


def _text(value: Any, field: str, limit: int, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or len(value) > limit or (not value and not allow_empty):
        raise FixtureError(f"{field} must be bounded text")
    return value


def _has_type(kind: str, value: Any) -> bool:
    """Strict type test. bool is not int, null is not a missing key."""
    if kind == "bool":
        return type(value) is bool
    if kind == "int":
        return type(value) is int
    if kind == "string":
        return type(value) is str
    return kind == "null" and value is None


def validate_registry(doc: Any) -> dict:
    _exact(doc, {"schema", "notice", "observer_allowlist", "observations"}, (), "registry")
    if doc["schema"] != "outcome-evidence-observations-v1":
        raise FixtureError("registry schema is not recognized")
    allow = doc["observer_allowlist"]
    if not isinstance(allow, list) or not allow:
        raise FixtureError("observer_allowlist must be a non-empty list")
    observers = [_id(item, "observer_allowlist entry") for item in allow]
    if len(set(observers)) != len(observers):
        raise FixtureError("observer_allowlist has duplicates")
    rows = doc["observations"]
    if not isinstance(rows, list) or len(rows) > MAX_OBSERVATIONS:
        raise FixtureError("observations must be a bounded list")
    by_id: dict = {}
    for row in rows:
        _exact(
            row,
            {"observation_id", "observer", "case_id", "run_id", "requirement_id", "category"},
            {"observed_value"},
            "observation",
        )
        oid = _id(row["observation_id"], "observation_id")
        if oid in by_id:
            raise FixtureError(f"duplicate observation_id: {oid}")
        for field in ("observer", "case_id", "run_id", "requirement_id"):
            _id(row[field], f"observation {oid} {field}")
        _enum(row["category"], ALL_CATEGORIES, f"observation {oid} category")
        by_id[oid] = row
    return {"observers": frozenset(observers), "by_id": by_id}


def _validate_case(case: Any) -> None:
    _exact(
        case,
        {"case_id", "run_id", "raw_verdict", "evidence_text", "claimed_evidence_kind",
         "claimed_progress_percent", "requirements"},
        (),
        "case",
    )
    cid = _id(case["case_id"], "case_id")
    _id(case["run_id"], f"case {cid} run_id")
    _enum(case["raw_verdict"], OUTCOMES, f"case {cid} raw_verdict")
    _text(case["evidence_text"], f"case {cid} evidence_text", 512, allow_empty=True)
    _enum(case["claimed_evidence_kind"], ALL_CATEGORIES | {"none"}, f"case {cid} claimed_evidence_kind")
    pct = case["claimed_progress_percent"]
    if pct is not None and (type(pct) is not int or not 0 <= pct <= 100):
        raise FixtureError(f"case {cid} claimed_progress_percent must be null or 0..100")
    reqs = case["requirements"]
    if not isinstance(reqs, list) or not 1 <= len(reqs) <= MAX_REQUIREMENTS:
        raise FixtureError(f"case {cid} requirements must be a bounded non-empty list")
    seen = set()
    for req in reqs:
        _exact(
            req,
            {"requirement_id", "condition", "value_type", "required_value", "observation_ids"},
            (),
            f"case {cid} requirement",
        )
        rid = _id(req["requirement_id"], f"case {cid} requirement_id")
        if rid in seen:
            raise FixtureError(f"case {cid} duplicate requirement_id: {rid}")
        seen.add(rid)
        _text(req["condition"], f"requirement {rid} condition", 160)
        _enum(req["value_type"], VALUE_TYPES, f"requirement {rid} value_type")
        if not _has_type(req["value_type"], req["required_value"]):
            raise FixtureError(f"requirement {rid} required_value does not match value_type")
        ids = req["observation_ids"]
        if not isinstance(ids, list) or len(ids) > MAX_OBSERVATIONS:
            raise FixtureError(f"requirement {rid} observation_ids must be a list")
        for item in ids:
            _id(item, f"requirement {rid} observation id")
        if len(set(ids)) != len(ids):
            raise FixtureError(f"requirement {rid} repeats an observation id")


def validate_cases(doc: Any):
    """Return (cases, corrections_by_case_id). Raises FixtureError on any defect."""
    _exact(doc, {"schema", "notice", "cases", "corrections"}, (), "cases document")
    if doc["schema"] != "outcome-evidence-cases-v1":
        raise FixtureError("cases schema is not recognized")
    cases = doc["cases"]
    if not isinstance(cases, list) or not cases or len(cases) > MAX_CASES:
        raise FixtureError("cases must be a bounded non-empty list")
    case_ids, run_ids = set(), set()
    for case in cases:
        _validate_case(case)
        if case["case_id"] in case_ids:
            raise FixtureError(f"duplicate case_id: {case['case_id']}")
        if case["run_id"] in run_ids:
            raise FixtureError(f"duplicate run_id: {case['run_id']}")
        case_ids.add(case["case_id"])
        run_ids.add(case["run_id"])
    rows = doc["corrections"]
    if not isinstance(rows, list):
        raise FixtureError("corrections must be a list")
    by_case: dict = {}
    seen = set()
    for row in rows:
        _exact(
            row,
            {"correction_id", "case_id", "run_id", "raw_verdict", "corrected_verdict", "code"},
            {"support_observation_ids"},
            "correction",
        )
        corr = _id(row["correction_id"], "correction_id")
        cid = _id(row["case_id"], f"correction {corr} case_id")
        _id(row["run_id"], f"correction {corr} run_id")
        if corr in seen:
            raise FixtureError(f"duplicate correction_id: {corr}")
        if cid not in case_ids:
            raise FixtureError(f"correction {corr} names an unknown case")
        if cid in by_case:
            raise FixtureError(f"case {cid} has more than one correction record")
        seen.add(corr)
        by_case[cid] = row
    return cases, by_case


def validate_expected(doc: Any) -> dict:
    _exact(doc, {"schema", "notice", "cases"}, (), "expected document")
    if doc["schema"] != "outcome-evidence-expected-v1":
        raise FixtureError("expected schema is not recognized")
    if not isinstance(doc["cases"], dict):
        raise FixtureError("expected cases must be an object")
    for cid, row in doc["cases"].items():
        _id(cid, "expected case id")
        _exact(row, {"audited_status", "reason", "correction_status", "baseline_recording"}, (), f"expected {cid}")
        _enum(row["audited_status"], OUTCOMES, f"expected {cid} audited_status")
        _text(row["reason"], f"expected {cid} reason", 200)
        _enum(row["correction_status"], CORRECTION_STATUSES, f"expected {cid} correction_status")
        _enum(row["baseline_recording"], BASELINE_STATUSES, f"expected {cid} baseline_recording")
    return doc["cases"]


# ------------------------------------------------------------------ audit

def _requirement_result(req, status, reason, ids):
    return {
        "requirement_id": req["requirement_id"],
        "status": status,
        "reason": reason,
        "observation_ids": list(ids),
    }


def _audit_requirement(case: Mapping, req: Mapping, registry: Mapping) -> dict:
    """Judge one requirement from registry observations only.

    Any defect in any referenced observation makes the result unknown. A
    pasted evidence category in the case is never consulted.
    """
    ids = req["observation_ids"]
    if not ids:
        return _requirement_result(req, "unknown", "no_observation_pointer", ids)
    found = []
    for oid in ids:
        obs = registry["by_id"].get(oid)
        if obs is None:
            return _requirement_result(req, "unknown", f"unresolved_observation_pointer:{oid}", ids)
        for field, want in (
            ("case_id", case["case_id"]),
            ("run_id", case["run_id"]),
            ("requirement_id", req["requirement_id"]),
        ):
            if obs[field] != want:
                return _requirement_result(req, "unknown", f"observation_scope_mismatch_{field}:{oid}", ids)
        if obs["observer"] not in registry["observers"]:
            return _requirement_result(req, "unknown", f"observer_not_allowlisted:{oid}", ids)
        if obs["category"] not in PROOF_CATEGORIES:
            return _requirement_result(req, "unknown", f"non_proof_category:{oid}", ids)
        if "observed_value" not in obs:
            return _requirement_result(req, "unknown", f"observed_value_missing:{oid}", ids)
        if not _has_type(req["value_type"], obs["observed_value"]):
            return _requirement_result(req, "unknown", f"observed_value_type_mismatch:{oid}", ids)
        found.append(obs)
    matches = {obs["observed_value"] == req["required_value"] for obs in found}
    if len(matches) == 2:
        return _requirement_result(req, "unknown", "conflicting_observations", ids)
    if matches == {True}:
        return _requirement_result(req, "passed", "observed_state_matches_required", ids)
    return _requirement_result(req, "failed", "observed_state_differs_from_required", ids)


def _audit_correction(case: Mapping, record: Mapping, audit: Mapping) -> dict:
    support = record.get("support_observation_ids")
    out = {
        "correction_id": copy.deepcopy(record.get("correction_id")),
        "raw_verdict": copy.deepcopy(record.get("raw_verdict")),
        "corrected_verdict": copy.deepcopy(record.get("corrected_verdict")),
        "code": copy.deepcopy(record.get("code")),
        "support_observation_ids": copy.deepcopy(support),
    }

    def verdict(status, reason):
        return {"status": status, "reason": reason, **out}

    if record.get("raw_verdict") != case["raw_verdict"]:
        return verdict("rejected", "raw_verdict_mismatch")
    if record.get("case_id") != case["case_id"]:
        return verdict("rejected", "correction_scope_mismatch_case_id")
    if record.get("run_id") != case["run_id"]:
        return verdict("rejected", "correction_scope_mismatch_run_id")
    if case["raw_verdict"] != "failed":
        return verdict("rejected", "only_a_raw_failed_verdict_is_correctable")
    if record.get("corrected_verdict") != "passed":
        return verdict("rejected", "only_failed_to_passed_is_supported")
    code = record.get("code")
    if not isinstance(code, str) or code not in CORRECTION_CODES:
        return verdict("rejected", "unsupported_correction_code")
    if (
        not isinstance(support, list)
        or not support
        or not all(isinstance(item, str) for item in support)
        or len(set(support)) != len(support)
    ):
        return verdict("rejected", "missing_or_malformed_support_pointer")
    if audit["status"] != "passed":
        return verdict("rejected", f"observed_state_not_supported:{audit['reason']}")
    satisfying = set()
    for item in audit["requirements"]:
        satisfying.update(item["observation_ids"])
    for pointer in support:
        if pointer not in satisfying:
            return verdict("rejected", f"support_pointer_not_a_satisfying_observation:{pointer}")
    for item in audit["requirements"]:
        if not set(support) & set(item["observation_ids"]):
            return verdict("rejected", f"support_pointer_missing_for_requirement:{item['requirement_id']}")
    return verdict("authorized", "correction_code_and_observed_state_support_present")


def audit_case(case: Mapping, registry: Mapping, correction: Optional[Mapping] = None) -> dict:
    """Audit one case against a validated registry. Takes no expectations.

    The input raw_verdict is reported unchanged. A correction is evaluated as
    a separate record and never alters the case, the raw verdict or the
    audited outcome.
    """
    _validate_case(case)
    reqs = [_audit_requirement(case, req, registry) for req in case["requirements"]]
    statuses = [item["status"] for item in reqs]
    if "failed" in statuses:
        decider = reqs[statuses.index("failed")]
    elif "unknown" in statuses:
        decider = reqs[statuses.index("unknown")]
    else:
        decider = None
    status = decider["status"] if decider else "passed"
    reason = decider["reason"] if decider else "all_requirements_matched"
    pointers = []
    for item in reqs:
        pointers.extend(i for i in item["observation_ids"] if i not in pointers)
    audit = {"status": status, "reason": reason, "observation_ids": pointers, "requirements": reqs}
    if correction is None:
        corr = {"status": "none", "reason": "no_correction_record"}
    else:
        corr = _audit_correction(case, correction, audit)
    return {
        "case_id": case["case_id"],
        "run_id": case["run_id"],
        "raw_verdict": case["raw_verdict"],
        "untrusted_claimed_evidence_kind": case["claimed_evidence_kind"],
        "audited_outcome": audit,
        "correction": corr,
    }


def audit_documents(cases_doc: Any, observations_doc: Any) -> list:
    registry = validate_registry(observations_doc)
    cases, corrections = validate_cases(cases_doc)
    known = {case["case_id"] for case in cases}
    for oid in sorted(registry["by_id"]):
        if registry["by_id"][oid]["case_id"] not in known:
            raise FixtureError(f"observation {oid} names an unknown case")
    return [audit_case(case, registry, corrections.get(case["case_id"])) for case in cases]


def unreferenced_observations(cases_doc: Mapping, observations_doc: Mapping) -> list:
    used = {
        oid
        for case in cases_doc["cases"]
        for req in case["requirements"]
        for oid in req["observation_ids"]
    }
    return sorted(row["observation_id"] for row in observations_doc["observations"] if row["observation_id"] not in used)


# --------------------------------------------------------------- baseline

_CHECKPOINT_MODULE = "shared_work_checkpoint_baseline"


def load_checkpoint(expected_sha=None):
    """Import the shipped checkpoint module without writing bytecode beside it."""
    fingerprint = (str(CHECKPOINT_PATH.resolve()), _sha(_read(CHECKPOINT_PATH, "checkpoint module")))
    if expected_sha is not None and fingerprint[1] != expected_sha:
        raise FixtureError("baseline source changed during report preparation")
    if _CHECKPOINT_MODULE in sys.modules:
        cached = sys.modules[_CHECKPOINT_MODULE]
        if getattr(cached, "_outcome_source_fingerprint", None) != fingerprint:
            raise FixtureError("baseline source changed; start a fresh process")
        return cached
    spec = importlib.util.spec_from_file_location(_CHECKPOINT_MODULE, CHECKPOINT_PATH)
    if spec is None or spec.loader is None:
        raise FixtureError("shipped checkpoint module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[_CHECKPOINT_MODULE] = module
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
        if _sha(_read(CHECKPOINT_PATH, "checkpoint module")) != fingerprint[1]:
            raise FixtureError("baseline source changed during import")
        module._outcome_source_fingerprint = fingerprint
    except BaseException:
        sys.modules.pop(_CHECKPOINT_MODULE, None)
        raise
    finally:
        sys.dont_write_bytecode = previous
    return module


def baseline_recording(case: Mapping, checkpoint, fixture: Mapping) -> dict:
    """Open a fresh scope in a temporary store and try to record completion.

    Calls the real WorkCheckpointStore. The result describes recording
    behavior only.
    """
    cid = case["case_id"]
    expected_errors = (ValueError, KeyError, PermissionError, RuntimeError)
    with tempfile.TemporaryDirectory(prefix="outcome_evidence_") as tmp:
        store = checkpoint.WorkCheckpointStore(Path(tmp) / "work.jsonl")
        scope = checkpoint.WorkScope(**{**fixture["scope"], "work_id": cid})
        try:
            contracts = checkpoint.stage_contracts(
                copy.deepcopy(fixture["planning_members"]),
                copy.deepcopy(fixture["implementation_members"]),
            )
            store.open(
                scope,
                operation_id="open-1",
                source="operator_request",
                provenance=[f"task:{cid}"],
                authority=copy.deepcopy(fixture["authority"]),
                contracts=contracts,
                plan=copy.deepcopy(fixture["plan"]),
                remaining=["completion"],
                next_action="record_completion",
                evidence=["rules:verified"],
                occurred_at=FIXED_TIME,
            )
        except expected_errors as exc:
            raise FixtureError(f"baseline setup failed for {cid}: {type(exc).__name__}") from exc
        text = case["evidence_text"]
        try:
            store.record(
                scope,
                operation_id="complete-1",
                kind="completion",
                source="synthetic_agent",
                provenance=[f"case:{cid}"],
                evidence=[text] if text else [],
                remaining=[],
                next_action="",
                occurred_at=FIXED_TIME,
            )
        except expected_errors as exc:
            return {"recording": "rejected", "detail": f"{type(exc).__name__}: {exc}"}
    return {"recording": "accepted", "detail": "completion checkpoint recorded"}


# ----------------------------------------------------------- verification

def verify_expectations(results: list, baseline: Mapping, expected: Mapping) -> list:
    """Compare finished results with fixture expectations. Runs after the audit."""
    mismatches = []
    got_ids = {item["case_id"] for item in results}
    for cid in sorted(got_ids - set(expected)):
        mismatches.append(f"{cid}: no expectation")
    for cid in sorted(set(expected) - got_ids):
        mismatches.append(f"{cid}: expectation has no case")
    for item in results:
        want = expected.get(item["case_id"])
        if want is None:
            continue
        got = {
            "audited_status": item["audited_outcome"]["status"],
            "reason": item["audited_outcome"]["reason"],
            "correction_status": item["correction"]["status"],
            "baseline_recording": baseline[item["case_id"]]["recording"],
        }
        for key in sorted(got):
            if got[key] != want[key]:
                mismatches.append(f"{item['case_id']}: {key} expected {want[key]} got {got[key]}")
    return mismatches


# ----------------------------------------------------------------- report

def run(cases_path=CASES_PATH, observations_path=OBSERVATIONS_PATH, expected_path=EXPECTED_PATH) -> dict:
    self_bytes = _read(Path(__file__).resolve(), "benchmark.py")
    blobs = {
        "cases": _read(cases_path, "cases"),
        "observations": _read(observations_path, "observations"),
        "expected": _read(expected_path, "expected"),
        "checkpoint": _read(CHECKPOINT_PATH, "checkpoint module"),
        "checkpoint_fixture": _read(CHECKPOINT_FIXTURE_PATH, "checkpoint fixture"),
    }
    cases_doc = parse_json(blobs["cases"], "cases")
    observations_doc = parse_json(blobs["observations"], "observations")
    expected_doc = parse_json(blobs["expected"], "expected")
    fixture = parse_json(blobs["checkpoint_fixture"], "checkpoint fixture")

    results = audit_documents(cases_doc, observations_doc)  # no expectations passed
    expected = validate_expected(expected_doc)
    checkpoint = load_checkpoint(expected_sha=_sha(blobs["checkpoint"]))
    baseline = {
        case["case_id"]: baseline_recording(case, checkpoint, fixture)
        for case in cases_doc["cases"]
    }
    for item in results:
        item["baseline_checkpoint"] = baseline[item["case_id"]]
    mismatches = verify_expectations(results, baseline, expected)

    def tally(values):
        return dict(sorted(Counter(values).items()))

    requirements = sum(len(case["requirements"]) for case in cases_doc["cases"])
    return {
        "schema": "outcome-evidence-report-v1",
        "experimental_notice": NOTICE,
        "baseline_note": BASELINE_NOTE,
        "inputs": {
            "benchmark": {"file_name": "benchmark.py", "sha256": _sha(self_bytes)},
            "cases": {"file_name": Path(cases_path).name, "sha256": _sha(blobs["cases"])},
            "observations": {"file_name": Path(observations_path).name, "sha256": _sha(blobs["observations"])},
            "expected": {"file_name": Path(expected_path).name, "sha256": _sha(blobs["expected"])},
        },
        "record_counts": {
            "cases": len(cases_doc["cases"]),
            "requirements": requirements,
            "observations": len(observations_doc["observations"]),
            "allowlisted_observers": len(observations_doc["observer_allowlist"]),
            "corrections": len(cases_doc["corrections"]),
            "expectations": len(expected),
        },
        "baseline_source": {
            "module": CHECKPOINT_LABEL,
            "sha256": _sha(blobs["checkpoint"]),
            "fixture": CHECKPOINT_FIXTURE_LABEL,
            "fixture_sha256": _sha(blobs["checkpoint_fixture"]),
        },
        "unreferenced_observation_ids": unreferenced_observations(cases_doc, observations_doc),
        "cases": results,
        "fixture_tallies": {
            "audited_status": tally(item["audited_outcome"]["status"] for item in results),
            "correction_status": tally(item["correction"]["status"] for item in results),
            "baseline_recording": tally(item["recording"] for item in baseline.values()),
        },
        "fixture_verification": {"passed": not mismatches, "mismatches": mismatches},
    }


def _selftest() -> int:
    suite = unittest.defaultTestLoader.discover(
        str(HERE), pattern="test_benchmark.py", top_level_dir=str(HERE)
    )
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--cases", default=str(CASES_PATH))
    parser.add_argument("--observations", default=str(OBSERVATIONS_PATH))
    parser.add_argument("--expected", default=str(EXPECTED_PATH))
    parser.add_argument("--selftest", action="store_true", help="run test_benchmark.py")
    args = parser.parse_args(argv)
    if args.selftest:
        return _selftest()
    try:
        report = run(args.cases, args.observations, args.expected)
    except FixtureError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0 if report["fixture_verification"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
