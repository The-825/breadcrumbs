#!/usr/bin/env python3
"""Guard: every text file decodes as strict UTF-8.

One pasted Latin-1 or Windows-1252 byte (a middle dot, a curly quote, a
non-breaking space) makes a file unreadable to any tool that opens it with
encoding="utf-8", and most of the other guards skip a file they cannot decode
rather than fail on it. So the damage is double: the file breaks its readers,
and it silently drops out of every scan that was supposed to cover it. This
guard fails on the first undecodable byte and names its line.

Assumes: Python 3.9+, stdlib only. Text files are picked by extension; edit
EXTS for your repo.

Usage:
    guard_valid_utf8.py [path ...]
No args -> CI mode: scans DEFAULT_PATHS with DEFAULT_EXCLUDE applied.
Explicit path -> self-test mode: exclusions are skipped, so the guard bites a
bad fixture handed to it directly. Exit 1 on violation, 0 if clean.
"""
import os
import sys

# ---- Configuration: edit for your repo layout --------------------------------
DEFAULT_PATHS = ["."]  # trees scanned in CI mode (no args)
DEFAULT_EXCLUDE = ("ci-kit/guards/tests/bad_fixtures/", "/.git/", "__pycache__",
                   "/node_modules/")
EXTS = (".md", ".txt", ".py", ".sh", ".json", ".jsonl", ".yml", ".yaml", ".toml",
        ".html", ".css", ".js", ".sql", ".tsv", ".csv", ".example")
# -------------------------------------------------------------------------------


def _iter_files(paths, apply_exclude):
    for p in paths:
        if os.path.isfile(p):
            if p.endswith(EXTS):
                yield p
        elif os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for name in files:
                    if not name.endswith(EXTS):
                        continue
                    fp = os.path.join(root, name)
                    if apply_exclude and any(x in fp.replace("\\", "/") for x in DEFAULT_EXCLUDE):
                        continue
                    yield fp


def check_file(fp):
    try:
        with open(fp, "rb") as f:
            data = f.read()
    except OSError as exc:
        return [(fp, 0, f"unreadable: {exc}")]
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        line = data.count(b"\n", 0, exc.start) + 1
        return [(fp, line, f"invalid UTF-8 byte 0x{data[exc.start]:02x}: "
                           "re-save the file as UTF-8")]
    return []


def main(argv):
    args = argv[1:]
    apply_exclude = not args
    paths = args if args else DEFAULT_PATHS
    fail = 0
    for fp in _iter_files(paths, apply_exclude):
        for path, line, msg in check_file(fp):
            print(f"{path}:{line}: {msg}")
            fail = 1
    print("guard_valid_utf8: " + ("FAILED" if fail else "clean"))
    return fail


if __name__ == "__main__":
    sys.exit(main(sys.argv))
