"""Promote portable repository identities into evidence-backed detailed reviews."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANDSCAPE = ROOT / "docs" / "collaborative-intelligence-repository-landscape.json"
MANIFEST = ROOT / "docs" / "collaborative-intelligence-repository-wave-r4-reviews.json"
PROMOTED_FIELDS = (
    "snapshot_commit", "snapshot_date", "stars_observed", "selection_aspect",
    "category", "lifecycle", "evidence_depth", "evidence_pointer",
    "evidence_note", "claims", "mechanisms", "stars_observed_date",
)


def key(value: str) -> str:
    return value.removesuffix(".git").casefold()


def read_git_json(ref: str, path: str) -> dict:
    payload = subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT)
    return json.loads(payload.decode("utf-8"))


def fetch_readme(review: dict) -> tuple[str, str]:
    owner_repo = review["repository"]
    revision = review["snapshot_commit"]
    candidates = [review["evidence_pointer"], "README.md", "README.MD", "readme.md"]
    for candidate in dict.fromkeys(candidates):
        url = f"https://raw.githubusercontent.com/{owner_repo}/{revision}/{candidate}"
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "breadcrumbs-review-validator"})
            with urllib.request.urlopen(request, timeout=20) as response:
                content = response.read()
            return candidate, hashlib.sha256(content).hexdigest()
        except Exception:
            continue
    raise ValueError(f"{owner_repo}: pinned README is not publicly retrievable")


def bootstrap(ref: str) -> dict:
    current = json.loads(LANDSCAPE.read_text(encoding="utf-8"))
    prior = read_git_json(ref, "docs/collaborative-intelligence-repository-landscape.json")
    current_rows = {key(row["repository"]): row for row in current["repositories"]}
    aliases = {
        key(alias["key"]): row
        for row in current["repositories"]
        for alias in row.get("aliases", [])
    }
    reviews = []
    for row in prior["repositories"]:
        if row.get("evidence_depth") != "readme-screened" or int(row["id"].split("-")[1]) <= 100:
            continue
        target = current_rows.get(key(row["repository"])) or aliases.get(key(row["repository"]))
        if target is None:
            raise ValueError(f"unmatched review: {row['repository']}")
        review = {field: row[field] for field in PROMOTED_FIELDS}
        review.update(
            {
                "repository": target["repository"],
                "repository_id": target["id"],
                "review_basis": "manual-readme-screening",
                "authority": "descriptive-only",
            }
        )
        reviews.append(review)
    if len(reviews) != 106 or len({row["repository_id"] for row in reviews}) != 106:
        raise ValueError("expected exactly 106 unique Wave R4 review promotions")
    with ThreadPoolExecutor(max_workers=12) as pool:
        evidence = list(pool.map(fetch_readme, reviews))
    for review, (pointer, digest) in zip(reviews, evidence):
        review["evidence_pointer"] = pointer
        review["readme_sha256"] = digest
    return {
        "schema_version": "1.0",
        "review_wave": "R4",
        "source_ref": ref,
        "review_count": len(reviews),
        "promotion_policy": "portable identity is retained whether or not detailed review is promoted",
        "authority": "descriptive-only",
        "reviews": sorted(reviews, key=lambda row: row["repository_id"]),
    }


def validate_manifest(manifest: dict, landscape: dict) -> list[str]:
    errors = []
    if manifest.get("schema_version") != "1.0":
        errors.append("unsupported review manifest schema")
    reviews = manifest.get("reviews", [])
    if manifest.get("review_count") != len(reviews) or len(reviews) != 106:
        errors.append("review count must be exactly 106")
    rows = {row["id"]: row for row in landscape["repositories"]}
    if len({review.get("repository_id") for review in reviews}) != len(reviews):
        errors.append("review repository IDs are not unique")
    for review in reviews:
        location = review.get("repository_id", "unknown")
        target = rows.get(location)
        if target is None or target["repository"] != review.get("repository"):
            errors.append(f"{location}: review target does not match current ledger")
        if review.get("evidence_depth") != "readme-screened":
            errors.append(f"{location}: invalid evidence depth")
        if review.get("authority") != "descriptive-only":
            errors.append(f"{location}: review grants authority")
        if not re.fullmatch(r"[0-9a-f]{40}", review.get("snapshot_commit", "")):
            errors.append(f"{location}: review is not pinned")
        if not re.fullmatch(r"[0-9a-f]{64}", review.get("readme_sha256", "")):
            errors.append(f"{location}: README digest is missing")
        if not review.get("claims") or set(review.get("mechanisms", {})) != set(landscape["dimensions"]):
            errors.append(f"{location}: detailed appraisal is incomplete")
    return errors


def apply_promotions(landscape: dict, manifest: dict) -> dict:
    rows = {row["id"]: row for row in landscape["repositories"]}
    for review in manifest["reviews"]:
        target = rows[review["repository_id"]]
        portable = target.get("portable_assessments", [])
        aliases = target.get("aliases", [])
        license_status = target.get("license_status", "unknown")
        upstream_revision = target.get("upstream_revision", "unknown")
        for field in PROMOTED_FIELDS:
            target[field] = review[field]
        target["assessment_status"] = "mechanism-screened"
        target["portable_assessments"] = portable
        target["aliases"] = aliases
        target["license_status"] = license_status
        target["upstream_revision"] = upstream_revision
        target["detailed_review"] = {
            "wave": manifest["review_wave"],
            "basis": review["review_basis"],
            "readme_sha256": review["readme_sha256"],
            "authority": review["authority"],
        }
    detailed = sum(row["evidence_depth"] == "readme-screened" for row in rows.values())
    portable = sum(row["evidence_depth"] == "source-assessment" for row in rows.values())
    landscape["review_summary"] = {
        "detailed_appraisal_count": detailed,
        "portable_only_count": portable,
        "total_repository_count": len(rows),
        "latest_review_wave": manifest["review_wave"],
        "latest_review_wave_count": len(manifest["reviews"]),
    }
    return landscape


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap-ref")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.bootstrap_ref:
        manifest = bootstrap(args.bootstrap_ref)
        if args.write:
            MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    landscape = json.loads(LANDSCAPE.read_text(encoding="utf-8"))
    errors = validate_manifest(manifest, landscape)
    if errors:
        print("\n".join(f"repository_review_promotions: {error}" for error in errors))
        return 1
    updated = apply_promotions(landscape, manifest)
    if args.write:
        LANDSCAPE.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    summary = updated["review_summary"]
    print("repository_review_promotions: " + " ".join(f"{key}={value}" for key, value in summary.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
