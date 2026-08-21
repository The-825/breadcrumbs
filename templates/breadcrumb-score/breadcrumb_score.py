#!/usr/bin/env python3
"""Validate and score a Breadcrumb Score assessment.

Assumptions: Python 3.9+, JSON input, and human-reviewed evidence records.
Ships: yes. This file is a copyable standard-library reference implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping


VERSION = "0.1.0"
DIMENSIONS = (
    "discoverability",
    "capability_evidence",
    "memory_continuity",
    "provenance_trust",
    "correction_behavior",
    "delegation_contract",
    "safety_approval",
    "outcome_reliability",
)
EVIDENCE_CLASSES = {"declared", "observed", "tested", "independently_verified"}
PUBLIC_STATUSES = {"owner_reviewed", "published"}


class AssessmentError(ValueError):
    """Raised when an assessment cannot be scored safely."""


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(assessment: Mapping[str, Any]) -> None:
    """Fail closed when required identity, evidence, or review fields are absent."""
    if assessment.get("schema_version") != VERSION:
        raise AssessmentError(f"schema_version must be {VERSION}")

    target = assessment.get("target")
    if not isinstance(target, Mapping):
        raise AssessmentError("target must be an object")
    for field in ("name", "owner", "purpose", "evidence_scope"):
        if not _nonempty(target.get(field)):
            raise AssessmentError(f"target.{field} is required")

    if assessment.get("owner_opt_in") is not True:
        raise AssessmentError("owner_opt_in must be true")
    if not _nonempty(assessment.get("assessed_at")):
        raise AssessmentError("assessed_at is required")

    status = assessment.get("status", "draft")
    if status in PUBLIC_STATUSES and assessment.get("human_reviewed") is not True:
        raise AssessmentError("public-ready status requires human_reviewed=true")
    if status == "published" and not _nonempty(assessment.get("publication_approval")):
        raise AssessmentError("published status requires publication_approval")

    dimensions = assessment.get("dimensions")
    if not isinstance(dimensions, Mapping):
        raise AssessmentError("dimensions must be an object")
    extra = set(dimensions) - set(DIMENSIONS)
    if extra:
        raise AssessmentError(f"unknown dimensions: {', '.join(sorted(extra))}")

    for name in DIMENSIONS:
        record = dimensions.get(name)
        if not isinstance(record, Mapping):
            raise AssessmentError(f"dimensions.{name} is required")
        score = record.get("score")
        if score is None:
            if record.get("evidence"):
                raise AssessmentError(f"dimensions.{name} has evidence but no score")
            continue
        if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
            raise AssessmentError(f"dimensions.{name}.score must be null or an integer from 1 to 5")
        evidence_class = record.get("evidence_class")
        if evidence_class not in EVIDENCE_CLASSES:
            raise AssessmentError(f"dimensions.{name}.evidence_class is invalid")
        evidence = record.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise AssessmentError(f"dimensions.{name} requires evidence")
        for index, item in enumerate(evidence):
            if not isinstance(item, Mapping):
                raise AssessmentError(f"dimensions.{name}.evidence[{index}] must be an object")
            for field in ("claim", "source", "observed_at"):
                if not _nonempty(item.get(field)):
                    raise AssessmentError(
                        f"dimensions.{name}.evidence[{index}].{field} is required"
                    )


def score(assessment: Mapping[str, Any]) -> Dict[str, Any]:
    """Return deterministic coverage and readiness without treating unknown as failure."""
    validate(assessment)
    scored = [
        (name, assessment["dimensions"][name]["score"])
        for name in DIMENSIONS
        if assessment["dimensions"][name].get("score") is not None
    ]
    coverage = len(scored) / len(DIMENSIONS)
    weighted = sum(value for _, value in scored) / len(scored) if len(scored) >= 5 else None
    readiness = _readiness_band(weighted, coverage)
    canonical = json.dumps(assessment, sort_keys=True, separators=(",", ":"))
    return {
        "evaluator_version": VERSION,
        "target": assessment["target"]["name"],
        "status": assessment.get("status", "draft"),
        "evidence_coverage": round(coverage, 4),
        "tested_dimensions": len(scored),
        "weighted_score": round(weighted, 2) if weighted is not None else None,
        "readiness_band": readiness,
        "dimension_scores": {name: value for name, value in scored},
        "assessment_digest": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    }


def _readiness_band(weighted: float | None, coverage: float) -> str:
    if weighted is None or coverage < 0.625:
        return "insufficient_evidence"
    if weighted < 2:
        return "emerging"
    if weighted < 3.5:
        return "operational"
    if weighted < 4.5:
        return "governed"
    return "strong_evidence"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and calculate a Breadcrumb Score")
    parser.add_argument("assessment", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.assessment.read_text(encoding="utf-8"))
        result = score(payload)
    except (OSError, json.JSONDecodeError, AssessmentError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

