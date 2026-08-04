#!/usr/bin/env python3
"""Guard: env vars are read only in the central config registry.

os.environ / os.getenv anywhere in the scanned tree EXCEPT the config registry
file fails this guard. All env reads centralize in one frozen config registry
so a new deployment overrides one documented file and nothing else hardcodes a
lookup.

Test directories are exempt in the default scan (a test harness setting env for
its fakes is infra, not app config), but an explicitly-passed file is always
checked so the guard's own bad fixture bites.

Known limitation: this is a regex scan, not a real AST walk, so it also matches
inside comments and string literals. That trade-off keeps the guard at zero
dependencies and sub-second runtime; if you want precision, swap the line loop
for an ast.NodeVisitor that walks Attribute/Call nodes.

Usage:
    guard_env_var_in_config.py [path ...]
No args -> CI mode: scans DEFAULT_PATHS (skipping the config registry and test
dirs). Explicit path -> self-test mode: exclusions are skipped. Exit 1 on any
violation, 0 if clean.
"""
import os
import re
import sys

# ---- Configuration: edit for your repo layout --------------------------------
DEFAULT_PATHS = ["backend"]  # trees scanned in CI mode (no args)
DEFAULT_EXCLUDE = ("ci-kit/guards/tests/bad_fixtures/", "/.git/", "__pycache__", "/tests/")
CONFIG_REGISTRY_FILENAME = "config.py"  # the one file allowed to read the environment
# -------------------------------------------------------------------------------

ENV_RE = re.compile(r"\bos\.(environ|getenv)\b")


def _is_config(fp):
    return os.path.basename(fp) == CONFIG_REGISTRY_FILENAME


def _iter_files(paths, apply_exclude):
    for p in paths:
        if os.path.isfile(p):
            if p.endswith(".py"):
                yield p
        elif os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for name in files:
                    if not name.endswith(".py"):
                        continue
                    fp = os.path.join(root, name)
                    if apply_exclude and any(x in fp.replace("\\", "/") for x in DEFAULT_EXCLUDE):
                        continue
                    yield fp


def check_file(fp):
    problems = []
    if _is_config(fp):
        return problems  # the config registry is the one allowed place, always
    try:
        with open(fp, encoding="utf-8") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, FileNotFoundError):
        return problems
    for i, line in enumerate(lines, 1):
        if ENV_RE.search(line):
            problems.append((fp, i, f"env read outside {CONFIG_REGISTRY_FILENAME}: read it in the config registry and import CONFIG"))
    return problems


def main(argv):
    args = argv[1:]
    apply_exclude = not args
    paths = args if args else DEFAULT_PATHS
    fail = 0
    for fp in _iter_files(paths, apply_exclude):
        for path, line, msg in check_file(fp):
            print(f"{path}:{line}: {msg}")
            fail = 1
    print("guard_env_var_in_config: " + ("FAILED" if fail else "clean"))
    return fail


if __name__ == "__main__":
    sys.exit(main(sys.argv))
