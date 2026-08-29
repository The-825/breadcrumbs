#!/usr/bin/env python3
"""kit_manifest_check.py: the manifest may not lie about the kit.

kit.json exists so a developer or their agent can adopt programmatically:
resolve a problem to artifacts, copy them, run their selftests. A manifest
row pointing at a file that does not exist, or a selftest command whose
script moved, converts that promise into a wild-goose chase, and manifest
rot is silent because nothing reads the manifest in this repo's own
workflow. This check makes the rot loud: every artifact path must exist,
every problem-routing path must resolve to a listed location, and every
selftest command's script must exist. Runs in CI next to the selftests it
indexes.

Usage:
    python3 ci-kit/kit_manifest_check.py            # check ./kit.json
    python3 ci-kit/kit_manifest_check.py --selftest
"""

import json
import re
import runpy
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_OWNS = {
    "reusable-public-patterns-and-templates",
    "assessed-external-public-repository-metadata",
    "portable-repository-identity-and-provenance-intake",
}
REQUIRED_ACCEPTED = {
    "public-verified-repository-identity-and-provenance",
    "public-github-links",
    "public-license-and-upstream-revision",
    "public-safe-evidence-linked-aliases",
    "explicit-unknown-values",
    "generalized-workflows-and-mechanisms",
    "public-or-synthetic-tests",
}
REQUIRED_PROHIBITED = {
    "private-repository-identities",
    "operated-repository-identities",
    "source-context-repository-identity-as-transfer-row",
    "ferpa-student-or-staff-records",
    "internal-paths",
    "private-evidence",
    "credentials",
    "personal-or-household-data",
    "production-bound-schemas-or-queries",
}
REQUIRED_PROVENANCE = {
    "stable-repository-id",
    "stable-assessment-artifact-ids",
    "positive-public-visibility-proof",
    "public-source-links",
    "source-revision",
    "source-content-sha256",
    "explicit-nonauthorization",
}


def check_portfolio_contract(manifest: dict, root: Path) -> list[str]:
    failures = []
    contract = manifest.get("portfolio_contract")
    if not isinstance(contract, dict):
        return ["portfolio contract missing"]
    if contract.get("schema_version") != "1.0":
        failures.append("portfolio contract schema_version must be 1.0")
    if contract.get("canonical_owner") != "The-825/breadcrumbs":
        failures.append("portfolio contract canonical owner is not Breadcrumbs")
    if contract.get("role") != "reusable-public-pattern-and-assessment-owner":
        failures.append("portfolio contract role is incomplete")
    if set(contract.get("owns", [])) != REQUIRED_OWNS:
        failures.append("portfolio contract ownership capabilities are incomplete")
    if set(contract.get("source_retains", [])) != {
        "source-evidence", "private-records", "operational-authority"
    }:
        failures.append("portfolio contract must keep source evidence and authority external")
    if set(contract.get("accepted_data_classes", [])) != REQUIRED_ACCEPTED:
        failures.append("portfolio contract accepted data classes are incomplete")
    if set(contract.get("prohibited_data_classes", [])) != REQUIRED_PROHIBITED:
        failures.append("portfolio contract prohibited data classes are incomplete")

    transfer = contract.get("transfer_contract", {})
    entrypoint = transfer.get("entrypoint", "")
    if not entrypoint or not (root / entrypoint).is_file():
        failures.append("portfolio transfer entrypoint is missing")
    elif transfer.get("fail_closed") is not True:
        failures.append("portfolio transfer must fail closed")
    else:
        module = runpy.run_path(str(root / entrypoint))
        expected = {
            "PORTFOLIO_OWNER": contract.get("canonical_owner"),
            "TRANSFER_SCHEMA_VERSION": transfer.get("source_schema_version"),
            "LANDSCAPE_SCHEMA_VERSION": transfer.get("destination_schema_version"),
            "TRANSFER_RECORD_TYPE": transfer.get("required_record_type"),
            "TRANSFER_AUTHORITY": transfer.get("authority"),
        }
        for name, value in expected.items():
            if module.get(name) != value:
                failures.append(f"portfolio contract disagrees with importer constant {name}")
    if set(transfer.get("required_provenance", [])) != REQUIRED_PROVENANCE:
        failures.append("portfolio transfer provenance requirements are incomplete")
    if transfer.get("authority") != "evidence-only":
        failures.append("portfolio transfer must remain evidence-only")

    evidence = contract.get("evidence_classes", {})
    portable = evidence.get("portable_intake", {})
    detailed = evidence.get("detailed_appraisal", {})
    if portable != {
        "evidence_depth": "source-assessment",
        "may_expand": True,
        "claims_detailed_mechanism_review": False,
    }:
        failures.append("portable intake evidence class is incomplete")
    if detailed.get("evidence_depth") != "readme-screened" or detailed.get(
        "promotion_requires"
    ) != "named-mechanism-gap":
        failures.append("detailed appraisal promotion rule is incomplete")

    ledger_path = root / "docs" / "collaborative-intelligence-repository-landscape.json"
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"portfolio ledger unreadable: {exc}")
    else:
        rows = ledger.get("repositories", [])
        detailed_count = sum(
            row.get("evidence_depth") == detailed.get("evidence_depth") for row in rows
        )
        if detailed_count < detailed.get("saturation_baseline_count", 0):
            failures.append("detailed appraisal count is below its saturation baseline")
        if not any(row.get("evidence_depth") == portable.get("evidence_depth") for row in rows):
            failures.append("portable intake class is absent from the repository ledger")
        if ledger.get("schema_version") != transfer.get("destination_schema_version"):
            failures.append("portfolio contract disagrees with ledger schema version")
        summary = ledger.get("import_summary", {})
        if not re.fullmatch(r"[0-9a-f]{64}", summary.get("transfer_sha256", "")):
            failures.append("portfolio ledger lacks a valid source content hash")
        if not re.fullmatch(
            r"[0-9a-f]{40}", summary.get("transfer_upstream_revision", "")
        ):
            failures.append("portfolio ledger lacks a valid source revision")
        if summary.get("authority") != "descriptive-only":
            failures.append("portfolio ledger import summary grants authority")
    return failures


def check(manifest_path: Path, root: Path):
    """Returns a list of failure strings; empty means clean."""
    failures = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"kit.json unreadable: {exc}"]

    artifact_paths = set()
    for art in manifest.get("artifacts", []):
        path = art.get("path", "")
        artifact_paths.add(path)
        if not (root / path).exists():
            failures.append(f"artifact path missing: {path}")
        selftest = art.get("selftest")
        if selftest:
            script = next((tok for tok in selftest.split()
                           if tok.endswith(".py") or tok.endswith(".sh")), None)
            if script and not (root / script).exists():
                failures.append(f"selftest script missing: {script} ({path})")

    for problem, paths in manifest.get("problems", {}).items():
        for path in paths:
            if not (root / path).exists():
                failures.append(f"problem route missing: {path} ({problem!r})")

    for name in ("llms.txt", "README.md"):
        if not (root / name).exists():
            failures.append(f"companion file missing: {name}")

    failures.extend(check_portfolio_contract(manifest, root))

    # The manifest also may not lie about CI. kit.json tells adopters the
    # selftests run in this repo's own gate; without this check the manifest
    # and the workflow agree only because someone edited both (Atlas round 2,
    # 2026-08-09). Every selftest script named in the manifest must appear in
    # the CI workflow.
    ci = root / ".github" / "workflows" / "ci.yml"
    if ci.exists():
        ci_text = ci.read_text(encoding="utf-8")
        for art in manifest.get("artifacts", []):
            selftest = art.get("selftest")
            if not selftest:
                continue
            script = next((tok for tok in selftest.split()
                           if tok.endswith(".py") or tok.endswith(".sh")), None)
            if script and script not in ci_text:
                failures.append(
                    f"selftest not wired into CI: {script} "
                    f"(manifest claims it, ci.yml never runs it)")
    return failures


def selftest() -> int:
    checks = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "tool.py").write_text("# fixture\n")
        (root / "llms.txt").write_text("# fixture\n")
        (root / "README.md").write_text("# fixture\n")
        (root / "scripts").mkdir()
        (root / "scripts" / "repository_landscape.py").write_text(
            "PORTFOLIO_OWNER='The-825/breadcrumbs'\n"
            "TRANSFER_SCHEMA_VERSION='1.0'\n"
            "LANDSCAPE_SCHEMA_VERSION='2.0'\n"
            "TRANSFER_RECORD_TYPE='assessed_external_public_repository'\n"
            "TRANSFER_AUTHORITY='evidence-only'\n"
        )
        (root / "docs").mkdir()
        (root / "docs" / "collaborative-intelligence-repository-landscape.json").write_text(
            json.dumps({
                "schema_version": "2.0",
                "repositories": [
                    {"evidence_depth": "readme-screened"} for _ in range(100)
                ] + [{"evidence_depth": "source-assessment"}],
                "import_summary": {
                    "transfer_sha256": "a" * 64,
                    "transfer_upstream_revision": "b" * 40,
                    "authority": "descriptive-only",
                },
            })
        )
        contract = {
            "schema_version": "1.0",
            "canonical_owner": "The-825/breadcrumbs",
            "role": "reusable-public-pattern-and-assessment-owner",
            "owns": sorted(REQUIRED_OWNS),
            "source_retains": ["source-evidence", "private-records", "operational-authority"],
            "accepted_data_classes": sorted(REQUIRED_ACCEPTED),
            "prohibited_data_classes": sorted(REQUIRED_PROHIBITED),
            "transfer_contract": {
                "entrypoint": "scripts/repository_landscape.py",
                "source_schema_version": "1.0",
                "destination_schema_version": "2.0",
                "required_record_type": "assessed_external_public_repository",
                "required_provenance": sorted(REQUIRED_PROVENANCE),
                "authority": "evidence-only",
                "fail_closed": True,
            },
            "evidence_classes": {
                "portable_intake": {
                    "evidence_depth": "source-assessment",
                    "may_expand": True,
                    "claims_detailed_mechanism_review": False,
                },
                "detailed_appraisal": {
                    "evidence_depth": "readme-screened",
                    "saturation_baseline_count": 100,
                    "promotion_requires": "named-mechanism-gap",
                },
            },
        }
        good = {"portfolio_contract": contract,
                "artifacts": [{"path": "tool.py",
                               "selftest": "python3 tool.py --selftest"}],
                "problems": {"p": ["tool.py"]}}
        (root / "kit.json").write_text(json.dumps(good))
        checks.append(("a true manifest is clean",
                       check(root / "kit.json", root) == []))

        bad = {"portfolio_contract": contract,
               "artifacts": [{"path": "gone.py",
                              "selftest": "python3 also_gone.py --selftest"}],
               "problems": {"p": ["gone.py"]}}
        (root / "kit.json").write_text(json.dumps(bad))
        fails = check(root / "kit.json", root)
        checks.append(("a missing artifact path fails",
                       any("artifact path missing" in f for f in fails)))
        checks.append(("a missing selftest script fails",
                       any("selftest script missing" in f for f in fails)))
        checks.append(("a missing problem route fails",
                       any("problem route missing" in f for f in fails)))

        missing_owner = json.loads(json.dumps(good))
        del missing_owner["portfolio_contract"]["canonical_owner"]
        checks.append(("a missing portfolio owner fails closed",
                       bool(check_portfolio_contract(missing_owner, root))))

        unsafe = json.loads(json.dumps(good))
        unsafe["portfolio_contract"]["prohibited_data_classes"].remove(
            "ferpa-student-or-staff-records"
        )
        checks.append(("an incomplete prohibited-data boundary fails closed",
                       bool(check_portfolio_contract(unsafe, root))))

        (root / "kit.json").write_text(json.dumps(good))
        wf = root / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "ci.yml").write_text("steps:\n  run: echo no selftests here\n")
        fails = check(root / "kit.json", root)
        checks.append(("a manifest selftest absent from ci.yml fails",
                       any("not wired into CI" in f for f in fails)))
        (wf / "ci.yml").write_text("steps:\n  run: python3 tool.py --selftest\n")
        checks.append(("a manifest selftest present in ci.yml is clean",
                       check(root / "kit.json", root) == []))

        (root / "kit.json").write_text("{not json")
        checks.append(("unreadable json fails loudly, never passes",
                       bool(check(root / "kit.json", root))))

    failed = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(f"  {'ok  ' if ok else 'FAIL'}  {n}")
    print(f"selftest: {len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    failures = check(ROOT / "kit.json", ROOT)
    if failures:
        print(f"kit_manifest_check: {len(failures)} failure(s)")
        for f in failures:
            print(f"  {f}")
        return 1
    print("kit_manifest_check: clean (every path and selftest resolves)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
