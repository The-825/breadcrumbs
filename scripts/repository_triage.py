"""Record evidence-bounded triage for portable-only public repositories."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANDSCAPE = ROOT / "docs" / "collaborative-intelligence-repository-landscape.json"
MANIFEST = ROOT / "docs" / "collaborative-intelligence-repository-wave-r5-triage.json"
LOG_PATH = "docs/collaborative-intelligence-repository-collection-log.md"


def canonical(value: str) -> str:
    return value.removesuffix(".git").casefold()


def bootstrap(ref: str, landscape: dict) -> dict:
    text = subprocess.check_output(["git", "show", f"{ref}:{LOG_PATH}"], cwd=ROOT).decode("utf-8")
    candidates = {}
    for repository, url, reason in re.findall(
        r"\| \[([^\]]+)\]\((https://github\.com/[^)]+)\) \| (.*?) \|",
        text.replace("\n", " "),
    ):
        candidates[canonical(repository)] = {
            "repository": repository,
            "source_url": url,
            "reason": " ".join(reason.replace("—", ",").split()),
        }
    rows = [row for row in landscape["repositories"] if row["evidence_depth"] == "source-assessment"]
    reviews = []
    for row in rows:
        keys = [canonical(row["repository"]), *[canonical(alias["key"]) for alias in row.get("aliases", [])]]
        match = next((candidates[value] for value in keys if value in candidates), None)
        if match is None:
            raise ValueError(f"no prior public triage evidence for {row['repository']}")
        reviews.append(
            {
                "repository_id": row["id"],
                "repository": row["repository"],
                "source_url": row["url"],
                "status": "screened-not-promoted",
                "reason": match["reason"],
                "review_date": "2026-09-01",
                "review_basis": "public-readme-relevance-triage",
                "authority": "descriptive-only",
            }
        )
    if len(reviews) != 105:
        raise ValueError(f"expected 105 portable-only triage records, found {len(reviews)}")
    return {
        "schema_version": "1.0",
        "review_wave": "R5",
        "source_ref": ref,
        "triage_count": len(reviews),
        "promotion_boundary": "screened-not-promoted is a relevance disposition, not a quality score",
        "authority": "descriptive-only",
        "reviews": sorted(reviews, key=lambda row: row["repository_id"]),
    }


def validate(manifest: dict, landscape: dict) -> list[str]:
    errors = []
    portable = {row["id"]: row for row in landscape["repositories"] if row["evidence_depth"] == "source-assessment"}
    reviews = manifest.get("reviews", [])
    if manifest.get("schema_version") != "1.0" or manifest.get("triage_count") != 105:
        errors.append("triage manifest contract is invalid")
    if len(reviews) != 105 or len({row.get("repository_id") for row in reviews}) != 105:
        errors.append("triage must contain 105 unique records")
    if set(portable) != {row.get("repository_id") for row in reviews}:
        errors.append("triage must cover every and only portable-only record")
    for review in reviews:
        row = portable.get(review.get("repository_id"))
        if row is None or row["repository"] != review.get("repository"):
            errors.append(f"{review.get('repository_id')}: identity mismatch")
        if review.get("status") != "screened-not-promoted" or review.get("authority") != "descriptive-only":
            errors.append(f"{review.get('repository_id')}: invalid disposition")
        if not review.get("reason") or "—" in review.get("reason", ""):
            errors.append(f"{review.get('repository_id')}: reason is missing or malformed")
    return errors


def apply(landscape: dict, manifest: dict) -> dict:
    rows = {row["id"]: row for row in landscape["repositories"]}
    for review in manifest["reviews"]:
        rows[review["repository_id"]]["detailed_review_triage"] = {
            "wave": manifest["review_wave"],
            "status": review["status"],
            "reason": review["reason"],
            "review_date": review["review_date"],
            "review_basis": review["review_basis"],
            "authority": review["authority"],
        }
    landscape["review_summary"]["portable_only_triaged_count"] = len(manifest["reviews"])
    return landscape


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap-ref")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    landscape = json.loads(LANDSCAPE.read_text(encoding="utf-8"))
    manifest = bootstrap(args.bootstrap_ref, landscape) if args.bootstrap_ref else json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = validate(manifest, landscape)
    if args.check:
        current = {row["id"]: row for row in landscape["repositories"]}
        for review in manifest.get("reviews", []):
            expected = {
                "wave": manifest["review_wave"],
                "status": review["status"],
                "reason": review["reason"],
                "review_date": review["review_date"],
                "review_basis": review["review_basis"],
                "authority": review["authority"],
            }
            if current.get(review["repository_id"], {}).get("detailed_review_triage") != expected:
                errors.append(f"{review['repository_id']}: committed triage is stale")
    if errors:
        print("\n".join(f"repository_triage: {error}" for error in errors))
        return 1
    updated = apply(landscape, manifest)
    if args.write:
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        LANDSCAPE.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    print("repository_triage: portable_only=105 triaged=105 authority=descriptive-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
