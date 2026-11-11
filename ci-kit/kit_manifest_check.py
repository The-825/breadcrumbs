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

The manifest also may not stay silent. A shipped artifact with no manifest row
is invisible to anyone adopting through kit.json, and a check that only
verifies the rows already written never notices the row nobody wrote. So every
entry directly under the shipped roots (COVERED_ROOTS) must be named by an
artifact path or a problem route, or contain one.

Assumes: Python 3.9+, stdlib only. --run-selftests runs each manifest selftest
under the interpreter that started this script, which is how CI proves the
Python floor the manifest claims.

Usage:
    python3 ci-kit/kit_manifest_check.py                  # check ./kit.json
    python3 ci-kit/kit_manifest_check.py --selftest
    python3.9 ci-kit/kit_manifest_check.py --run-selftests
"""

import contextlib
import io
import json
import re
import runpy
import shlex
import subprocess
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
    split = contract.get("schema_version") == "1.1"
    if contract.get("schema_version") not in {"1.0", "1.1"}:
        failures.append("portfolio contract schema_version must be 1.0 or 1.1")
    if contract.get("canonical_owner") != "The-825/breadcrumbs":
        failures.append("portfolio contract canonical owner is not Breadcrumbs")
    expected_role = "reusable-public-pattern-owner" if split else "reusable-public-pattern-and-assessment-owner"
    if contract.get("role") != expected_role:
        failures.append("portfolio contract role is incomplete")
    expected_owns = {"reusable-public-patterns-and-templates", "workflow-guides", "prompt-library"} if split else REQUIRED_OWNS
    if set(contract.get("owns", [])) != expected_owns:
        failures.append("portfolio contract ownership capabilities are incomplete")
    if split:
        routing = contract.get("research_catalog", {})
        if routing.get("canonical_owner") != "The-825/staletoast" or routing.get("authority") != "evidence-only":
            failures.append("split catalog must have one evidence-only StaleToast owner")
        if routing.get("consumer_config") != "staletoast-consumer.json" or not (root / "staletoast-consumer.json").is_file():
            failures.append("split catalog requires a committed pinned consumer config")
        if contract.get("transfer_contract", {}).get("archive_only") is not True or contract.get("transfer_contract", {}).get("active_owner") != "The-825/staletoast":
            failures.append("legacy intake must route new records to StaleToast")
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
            "PRODUCER_CONTRACT_VERSION": transfer.get("producer_contract_version"),
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


# Roots whose direct children are shipped artifacts. docs/, skills/, checklists/
# and playbook/ are inventoried as whole suites, so they need no child check.
COVERED_ROOTS = ("templates", "ci-kit", "benchmarks")
# Index files and interpreter caches are not artifacts.
COVERAGE_EXEMPT = {"README.md", "__pycache__"}


def check_coverage(manifest: dict, root: Path) -> list[str]:
    """Every direct child of a shipped root is named in the manifest."""
    named = {art.get("path", "") for art in manifest.get("artifacts", [])}
    for paths in manifest.get("problems", {}).values():
        named.update(paths)
    failures = []
    for top in COVERED_ROOTS:
        base = root / top
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if child.name in COVERAGE_EXEMPT or child.name.startswith("."):
                continue
            rel = f"{top}/{child.name}"
            if not any(n == rel or n.startswith(rel + "/") for n in named):
                failures.append(
                    f"shipped but not inventoried: {rel} "
                    f"(add an artifact row or a problem route)")
    return failures


def run_selftests(manifest_path: Path, root: Path) -> int:
    """Run every manifest selftest under this interpreter. Returns failures."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    commands = []
    for art in manifest.get("artifacts", []):
        selftest = art.get("selftest")
        if selftest and selftest not in commands:
            commands.append(selftest)
    failed = 0
    for command in commands:
        argv = shlex.split(command)
        if argv and argv[0] in ("python3", "python"):
            argv[0] = sys.executable
        result = subprocess.run(argv, cwd=root, capture_output=True, text=True)
        print(f"  {'ok  ' if result.returncode == 0 else 'FAIL'}  {command}")
        if result.returncode:
            failed += 1
            tail = (result.stdout + result.stderr).strip().splitlines()[-15:]
            print("\n".join(f"        {line}" for line in tail))
    version = ".".join(str(part) for part in sys.version_info[:3])
    print(f"run-selftests: {len(commands) - failed}/{len(commands)} passed "
          f"on Python {version}")
    return failed


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
    failures.extend(check_coverage(manifest, root))

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
            "PRODUCER_CONTRACT_VERSION='2.0'\n"
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
                "producer_contract_version": "2.0",
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

        split = json.loads(json.dumps(good))
        split_contract = split['portfolio_contract']
        split_contract.update(schema_version='1.1', role='reusable-public-pattern-owner',
                              owns=['reusable-public-patterns-and-templates', 'workflow-guides', 'prompt-library'],
                              research_catalog={'canonical_owner': 'The-825/staletoast', 'authority': 'evidence-only',
                                                'consumer_config': 'staletoast-consumer.json'})
        split_contract['transfer_contract'].update(archive_only=True, active_owner='The-825/staletoast')
        (root / 'staletoast-consumer.json').write_text('{}')
        checks.append(('split ownership and archived importer are accepted', check_portfolio_contract(split, root) == []))
        split_contract['research_catalog']['canonical_owner'] = 'The-825/breadcrumbs'
        checks.append(('split duplicate research ownership fails closed', bool(check_portfolio_contract(split, root))))
        split_contract['research_catalog']['canonical_owner'] = 'The-825/staletoast'
        split_contract['transfer_contract']['archive_only'] = False
        checks.append(('split active legacy writer fails closed', bool(check_portfolio_contract(split, root))))

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

        (root / "templates").mkdir()
        (root / "templates" / "README.md").write_text("# index\n")
        (root / "templates" / "LISTED.md").write_text("# fixture\n")
        (root / "templates" / "suite").mkdir()
        (root / "templates" / "suite" / "tool.py").write_text("# fixture\n")
        (root / "templates" / "ORPHAN.md").write_text("# fixture\n")
        listed = {"artifacts": [{"path": "templates/suite/tool.py"}],
                  "problems": {"p": ["templates/LISTED.md"]}}
        fails = check_coverage(listed, root)
        checks.append(("a shipped file with no manifest row fails",
                       fails == ["shipped but not inventoried: templates/ORPHAN.md "
                                 "(add an artifact row or a problem route)"]))
        listed["artifacts"].append({"path": "templates/ORPHAN.md"})
        checks.append(("a directory is covered by an artifact inside it, "
                       "a file by a problem route, an index file by exemption",
                       check_coverage(listed, root) == []))

        (root / "pass.py").write_text("import sys\nsys.exit(0)\n")
        (root / "fail.py").write_text("import sys\nsys.exit(3)\n")
        runnable = {"artifacts": [{"path": "pass.py", "selftest": "python3 pass.py"},
                                  {"path": "fail.py", "selftest": "python3 fail.py"}]}
        (root / "run.json").write_text(json.dumps(runnable))
        with contextlib.redirect_stdout(io.StringIO()):
            ran = run_selftests(root / "run.json", root)
        checks.append(("--run-selftests counts a failing selftest", ran == 1))

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
    if "--run-selftests" in sys.argv:
        return 1 if run_selftests(ROOT / "kit.json", ROOT) else 0
    failures = check(ROOT / "kit.json", ROOT)
    if failures:
        print(f"kit_manifest_check: {len(failures)} failure(s)")
        for f in failures:
            print(f"  {f}")
        return 1
    print("kit_manifest_check: clean (every path and selftest resolves, "
          "every shipped artifact is inventoried)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
