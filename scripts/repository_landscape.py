"""Import and validate the public repository assessment ledger.

The committed landscape is the source of truth. A transfer manifest is an
evidence input only. Importing it never grants authority, installs software, or
creates work.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANDSCAPE = ROOT / "docs" / "collaborative-intelligence-repository-landscape.json"
PORTFOLIO_OWNER = "The-825/breadcrumbs"
TRANSFER_SCHEMA_VERSION = "1.0"
PRODUCER_CONTRACT_VERSION = "2.0"
LANDSCAPE_SCHEMA_VERSION = "2.0"
TRANSFER_RECORD_TYPE = "assessed_external_public_repository"
TRANSFER_AUTHORITY = "evidence-only"
PUBLIC_SOURCE_PREFIX = "https://github.com/"
DIMENSION_UNKNOWN = "U"
HEX_TO_LETTERS = str.maketrans("0123456789", "ghijklmnop")
FORBIDDEN_PUBLIC_FIELDS = {
    "source_path",
    "source_owner",
    "intended_owner",
    "data_boundary",
    "access_mode",
    "purpose",
    "notes",
}
REQUIRED_TRANSFER_FIELDS = {
    "stable_id",
    "canonical_key",
    "owner",
    "repo",
    "public_source_links",
    "source_artifact_ids",
    "assessment_date",
    "license",
    "upstream_revision",
    "authority",
    "source_content_sha256",
    "visibility",
    "verification_source",
    "verification_method",
    "verification_date",
    "source_revision",
    "license_status",
    "public_github_url",
}
FORBIDDEN_TRANSFER_FIELDS = {
    "source_path",
    "internal_path",
    "private_repository",
    "private_evidence",
    "credential",
    "student_record",
    "staff_record",
    "ferpa_record",
    "household_data",
    "personal_data",
    "production_schema",
    "production_query",
}


def canonical_key(value: str) -> str:
    parts = value.strip().removesuffix(".git").split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError(f"invalid repository identity: {value!r}")
    return "/".join(parts).casefold()


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{number}: {exc}") from exc
    return rows


def portable_source_id(row: dict) -> str:
    material = json.dumps(
        {
            "identity": row.get("canonical_key"),
            "assessment_date": row.get("assessment_date"),
            "source_links": sorted(
                row.get("public_source_links", row.get("source_links", [])),
                key=str.casefold,
            ),
            "disposition": row.get("disposition", ""),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(material.encode()).hexdigest()[:20]
    return "portable-source:" + digest.translate(HEX_TO_LETTERS)


def normalize_source_ids(data: dict) -> None:
    for row in data.get("repositories", []):
        for source in row.get("portable_assessments", []):
            prefix, separator, value = source.get("id", "").partition(":")
            if separator and prefix == "portable-source":
                source["id"] = prefix + ":" + value.translate(HEX_TO_LETTERS)
    for row in data.get("unresolved_identities", []):
        prefix, separator, value = row.get("source_id", "").partition(":")
        if separator and prefix == "portable-source":
            row["source_id"] = prefix + ":" + value.translate(HEX_TO_LETTERS)


def sanitized_source(row: dict, repository_url: str) -> dict:
    links = sorted(
        {
            repository_url,
            *row.get("public_source_links", row.get("source_links", [])),
        },
        key=lambda value: (value.casefold(), value),
    )
    aliases = []
    for alias in row.get("aliases", []):
        if not isinstance(alias, dict) or not alias.get("key") or not alias.get("evidence"):
            continue
        aliases.append(
            {
                "key": canonical_key(alias["key"]),
                "evidence": alias["evidence"],
            }
        )
    return {
        "id": portable_source_id(row),
        "repository_stable_id": row.get("stable_id"),
        "assessment_artifact_ids": sorted(row.get("source_artifact_ids", [])),
        "assessment_date": row.get("assessment_date"),
        "assessment_status": "assessed",
        "disposition": row.get("disposition") or "unresolved",
        "license_status": row.get("license") or "unknown",
        "upstream_revision": row.get("upstream_revision") or "unknown",
        "source_links": links,
        "aliases": aliases,
        "authority": TRANSFER_AUTHORITY,
        "visibility_proof": "public-github-source-link",
        "source_content_sha256": sorted(row["source_content_sha256"]),
        "verification_source": row["verification_source"],
        "verification_method": row["verification_method"],
        "verification_date": row["verification_date"],
    }


def validate_transfer_record(row: dict) -> None:
    if row.get("record_type") != TRANSFER_RECORD_TYPE:
        raise ValueError("transfer contains a non-external-public repository record")
    missing = sorted(REQUIRED_TRANSFER_FIELDS - set(row))
    if missing:
        raise ValueError(f"transfer record lacks required fields: {', '.join(missing)}")
    prohibited = sorted(FORBIDDEN_TRANSFER_FIELDS.intersection(row))
    if prohibited:
        raise ValueError(f"transfer record contains prohibited fields: {', '.join(prohibited)}")
    key = canonical_key(row["canonical_key"])
    if key != canonical_key(f"{row['owner']}/{row['repo']}"):
        raise ValueError("transfer identity does not match owner/repo")
    expected_url = f"{PUBLIC_SOURCE_PREFIX}{row['owner']}/{row['repo']}".casefold()
    links = row.get("public_source_links")
    if not isinstance(links, list) or not links:
        raise ValueError(f"{key}: positive public visibility proof is required")
    if any(not isinstance(link, str) or not link.startswith(PUBLIC_SOURCE_PREFIX) for link in links):
        raise ValueError(f"{key}: visibility proof must use public GitHub links")
    if expected_url not in {link.casefold() for link in links}:
        raise ValueError(f"{key}: canonical public repository link is required")
    if not row.get("source_artifact_ids") or not all(
        isinstance(value, str) and value for value in row["source_artifact_ids"]
    ):
        raise ValueError(f"{key}: stable assessment artifact IDs are required")
    if not isinstance(row.get("stable_id"), str) or not row["stable_id"]:
        raise ValueError(f"{key}: stable repository ID is required")
    if row["authority"] != TRANSFER_AUTHORITY:
        raise ValueError(f"{key}: transfer authority must remain evidence-only")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["assessment_date"]):
        raise ValueError(f"{key}: assessment date must be explicit")
    revision = row["upstream_revision"]
    if revision != "unknown" and not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError(f"{key}: upstream revision must be explicit or unknown")
    if row["visibility"] != "public":
        raise ValueError(f"{key}: visibility must be positively verified public")
    if row["public_github_url"].casefold() != expected_url:
        raise ValueError(f"{key}: verified public URL does not match canonical identity")
    verification_targets = {
        f"https://api.github.com/repos/{row['owner']}/{row['repo']}".casefold(),
        *{
            f"https://api.github.com/repos/{alias['key']}".casefold()
            for alias in row.get("aliases", [])
            if isinstance(alias, dict) and alias.get("key")
        },
    }
    if row["verification_source"].casefold() not in verification_targets:
        raise ValueError(f"{key}: GitHub verification source does not match identity")
    if row["source_revision"] != revision or revision == "unknown":
        raise ValueError(f"{key}: verified source revision must match upstream revision")
    hashes = row["source_content_sha256"]
    if not hashes or any(not re.fullmatch(r"[0-9a-f]{64}", value) for value in hashes):
        raise ValueError(f"{key}: canonical source content hashes are required")
    for alias in row.get("aliases", []):
        if not isinstance(alias, dict) or not alias.get("key") or not alias.get("evidence"):
            raise ValueError(f"{key}: aliases require public-safe evidence")


def reset_portable_import(data: dict) -> None:
    retained = []
    for row in data.get("repositories", []):
        if row.get("evidence_depth") == "source-assessment":
            continue
        row.pop("portable_assessments", None)
        row.pop("assessment_status", None)
        row.pop("license_status", None)
        row.pop("aliases", None)
        retained.append(row)
    data["repositories"] = retained
    data.pop("unresolved_identities", None)
    data.pop("import_summary", None)


def import_handoff(data: dict, handoff_path: Path, handoff_revision: str) -> dict:
    handoff_bytes = handoff_path.read_bytes()
    rows = read_jsonl(handoff_path)
    if not rows or rows[0].get("record_type") != "manifest":
        raise ValueError("transfer manifest must be the first JSONL record")
    manifest, source_rows = rows[0], rows[1:]
    if manifest.get("schema_version") != TRANSFER_SCHEMA_VERSION:
        raise ValueError("unsupported transfer schema")
    if manifest.get("producer_contract_version") != PRODUCER_CONTRACT_VERSION:
        raise ValueError("unsupported producer contract")
    if manifest.get("intended_owner") != PORTFOLIO_OWNER:
        raise ValueError("transfer is not addressed to the Breadcrumbs owner contract")
    if not re.fullmatch(r"[0-9a-f]{40}", handoff_revision):
        raise ValueError("transfer revision must be a full lowercase Git commit")

    reset_portable_import(data)
    for row in data["repositories"]:
        row["assessment_status"] = "mechanism-screened"
        row["license_status"] = "unknown"
        row["upstream_revision"] = row["snapshot_commit"]
        row["aliases"] = []

    dimensions = data["dimensions"]
    existing = {canonical_key(row["repository"]): row for row in data["repositories"]}
    next_id = max(int(row["id"].split("-")[1]) for row in existing.values()) + 1
    grouped: dict[str, list[dict]] = defaultdict(list)
    unresolved = []
    for row in source_rows:
        validate_transfer_record(row)
        key = canonical_key(row["canonical_key"])
        grouped[key].append(row)

    overlap = 0
    imported = 0
    source_count = 0
    for key in sorted(grouped):
        rows_for_key = grouped[key]
        sources = [
            sanitized_source(row, f"https://github.com/{key}") for row in rows_for_key
        ]
        source_count += sum(
            row.get("deduplication", {}).get("assessment_source_count", 1)
            for row in rows_for_key
        )
        matched_keys = {key} if key in existing else set()
        matched_keys.update(
            canonical_key(alias["key"])
            for row in rows_for_key
            for alias in row.get("aliases", [])
            if canonical_key(alias["key"]) in existing
        )
        if len(matched_keys) > 1:
            raise ValueError(f"{key}: aliases resolve to multiple existing repositories")
        if matched_keys:
            overlap += 1
            current = existing[next(iter(matched_keys))]
            current["portable_assessments"] = sorted(
                {item["id"]: item for item in [*current.get("portable_assessments", []), *sources]}.values(),
                key=lambda item: item["id"],
            )
            current.setdefault("assessment_status", "mechanism-screened")
            current.setdefault("license_status", "unknown")
            current.setdefault("aliases", [])
            if key != canonical_key(current["repository"]):
                current["aliases"] = sorted(
                    {alias["key"]: alias for alias in [
                        *current["aliases"],
                        {"key": key, "evidence": sources[0]["verification_source"]},
                    ]}.values(),
                    key=lambda alias: alias["key"],
                )
            continue

        first = rows_for_key[0]
        owner = first["owner"]
        repo = first["repo"]
        data["repositories"].append(
            {
                "id": f"R-{next_id:03d}",
                "repository": f"{owner}/{repo}",
                "url": f"https://github.com/{owner}/{repo}",
                "snapshot_commit": None,
                "snapshot_date": min(
                    row.get("assessment_date") or data["snapshot_date"]
                    for row in rows_for_key
                ),
                "stars_observed": None,
                "selection_aspect": "portfolio-memory-scout",
                "category": "unclassified",
                "lifecycle": "unknown",
                "evidence_depth": "source-assessment",
                "evidence_pointer": f"https://github.com/{owner}/{repo}",
                "evidence_note": "Repository identity and prior assessment disposition are preserved. Mechanism review, revision, and license remain unknown unless stated separately.",
                "claims": [],
                "mechanisms": {dimension: DIMENSION_UNKNOWN for dimension in dimensions},
                "assessment_status": "assessed",
                "license_status": next(
                    (row["license"] for row in rows_for_key if row.get("license") not in {None, "", "unknown"}),
                    "unknown",
                ),
                "upstream_revision": next(
                    (row["upstream_revision"] for row in rows_for_key if row.get("upstream_revision") not in {None, "", "unknown"}),
                    "unknown",
                ),
                "aliases": sorted(
                    {
                        alias["key"]: alias
                        for source in sources
                        for alias in source["aliases"]
                    }.values(),
                    key=lambda alias: alias["key"],
                ),
                "portable_assessments": sorted(sources, key=lambda item: item["id"]),
            }
        )
        existing[key] = data["repositories"][-1]
        next_id += 1
        imported += 1

    data["repositories"].sort(key=lambda row: int(row["id"].split("-")[1]))
    data["unresolved_identities"] = []
    data.pop("operated_repositories", None)
    data["schema_version"] = LANDSCAPE_SCHEMA_VERSION
    data["status_codes"] = ["V", "P", "N", "O", DIMENSION_UNKNOWN]
    data["snapshot_date"] = "2026-08-29"
    data["import_summary"] = {
        "transfer_schema_version": manifest["schema_version"],
        "producer_contract_version": manifest["producer_contract_version"],
        "transfer_sha256": hashlib.sha256(handoff_bytes).hexdigest(),
        "transfer_upstream_revision": handoff_revision,
        "transfer_record_count": len(source_rows),
        "assessment_source_count": source_count,
        "unique_resolved_transfer_repositories": len(grouped),
        "existing_repository_count_before": len(existing) - imported,
        "overlap_collapsed": overlap,
        "new_repositories_imported": imported,
        "unique_repository_count_after": len(existing),
        "transfer_duplicate_collapse_count": manifest.get("counts", {}).get(
            "duplicate_assessment_collapse_count", source_count - len(grouped)
        ),
        "unresolved_identity_count": 0,
        "unresolved_identity_count_excluded": manifest.get("counts", {}).get(
            "unresolved_identity_count_excluded", 0
        ),
        "supporting_reference_repository_count_excluded": manifest.get(
            "counts", {}
        ).get("supporting_reference_repository_count_excluded", 0),
        "excluded_portfolio_repository_count": manifest.get("counts", {}).get(
            "operated_repository_count_excluded", 0
        ),
        "unverified_or_nonpublic_repository_count_excluded": manifest.get(
            "counts", {}
        ).get("unverified_or_nonpublic_repository_count_excluded", 0),
        "license_unknown_count": sum(
            row.get("license_status") == "unknown" for row in data["repositories"]
        ),
        "upstream_revision_unknown_count": sum(
            row.get("upstream_revision", "unknown") == "unknown"
            for row in data["repositories"]
        ),
        "authority": "descriptive-only",
    }
    return data


def validate(data: dict) -> list[str]:
    errors = []
    rows = data.get("repositories", [])
    dimensions = data.get("dimensions", [])
    allowed = set(data.get("status_codes", []))
    keys = []
    ids = []
    aliases: dict[str, str] = {}
    def inspect_fields(value: object, location: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in FORBIDDEN_PUBLIC_FIELDS:
                    errors.append(f"{location}: forbidden public field {key}")
                inspect_fields(item, f"{location}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                inspect_fields(item, f"{location}[{index}]")

    inspect_fields(data, "landscape")
    for row in rows:
        try:
            key = canonical_key(row["repository"])
        except (KeyError, ValueError) as exc:
            errors.append(str(exc))
            continue
        keys.append(key)
        ids.append(row.get("id"))
        if row.get("url") != f"https://github.com/{row['repository']}":
            errors.append(f"{key}: URL does not match identity")
        if set(row.get("mechanisms", {})) != set(dimensions):
            errors.append(f"{key}: incomplete mechanism profile")
        if not set(row.get("mechanisms", {}).values()) <= allowed:
            errors.append(f"{key}: invalid mechanism status")
        for alias in row.get("aliases", []):
            if not alias.get("evidence"):
                errors.append(f"{key}: alias lacks evidence")
                continue
            alias_key = canonical_key(alias["key"])
            previous = aliases.setdefault(alias_key, key)
            if previous != key:
                errors.append(f"{key}: alias collision with {previous}")
        for source in row.get("portable_assessments", []):
            if source.get("authority") != TRANSFER_AUTHORITY:
                errors.append(f"{key}: portable source grants authority")
            if source.get("visibility_proof") != "public-github-source-link":
                errors.append(f"{key}: portable source lacks positive visibility proof")
            if not source.get("source_links"):
                errors.append(f"{key}: portable source lacks a public link")
            if not source.get("repository_stable_id"):
                errors.append(f"{key}: portable source lacks its stable repository ID")
            if not source.get("assessment_artifact_ids"):
                errors.append(f"{key}: portable source lacks assessment artifact IDs")
            if any(
                not link.startswith("https://github.com/")
                for link in source.get("source_links", [])
            ):
                errors.append(f"{key}: portable source link is not a public GitHub URL")
        revision = row.get("upstream_revision")
        if revision != "unknown" and not re.fullmatch(r"[0-9a-f]{40}", revision or ""):
            errors.append(f"{key}: invalid upstream revision")
        if not row.get("license_status"):
            errors.append(f"{key}: license status is required")
    if len(keys) != len(set(keys)):
        errors.append("repository identities are not unique case-insensitively")
    if len(ids) != len(set(ids)) or None in ids:
        errors.append("repository IDs are not unique")
    if set(keys).intersection(aliases):
        errors.append("an alias collides with a canonical repository identity")
    unresolved = data.get("unresolved_identities", [])
    if any(row.get("identity_status") != "unresolved" for row in unresolved):
        errors.append("unresolved identity register contains resolved data")
    if "operated_repositories" in data:
        errors.append("operated repository inventory must not be public")
    summary = data.get("import_summary", {})
    if summary and summary.get("unique_repository_count_after") != len(rows):
        errors.append("import summary unique count is stale")
    if summary and not re.fullmatch(
        r"[0-9a-f]{40}", summary.get("transfer_upstream_revision", "")
    ):
        errors.append("import summary lacks a valid transfer revision")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--import-handoff", type=Path)
    parser.add_argument("--handoff-revision")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = json.loads(LANDSCAPE.read_text(encoding="utf-8"))
    normalize_source_ids(data)
    if args.import_handoff:
        if not args.handoff_revision:
            parser.error("--handoff-revision is required with --import-handoff")
        data = import_handoff(data, args.import_handoff, args.handoff_revision)
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"repository_landscape: {error}")
        return 1
    if args.write:
        LANDSCAPE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    print(
        "repository_landscape: "
        f"repositories={len(data['repositories'])} "
        f"unresolved={len(data.get('unresolved_identities', []))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
