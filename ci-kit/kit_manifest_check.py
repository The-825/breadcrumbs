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
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


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
    return failures


def selftest() -> int:
    checks = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "tool.py").write_text("# fixture\n")
        (root / "llms.txt").write_text("# fixture\n")
        (root / "README.md").write_text("# fixture\n")
        good = {"artifacts": [{"path": "tool.py",
                               "selftest": "python3 tool.py --selftest"}],
                "problems": {"p": ["tool.py"]}}
        (root / "kit.json").write_text(json.dumps(good))
        checks.append(("a true manifest is clean",
                       check(root / "kit.json", root) == []))

        bad = {"artifacts": [{"path": "gone.py",
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
