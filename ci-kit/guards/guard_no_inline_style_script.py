#!/usr/bin/env python3
"""Guard: no inline <style> or inline <script> in HTML.

CSS goes to your stylesheet file; JS is ES modules loaded via
<script type="module" src="...">. An inline <style> block or an inline
<script> (one with body content, i.e. no src=) fails this guard. This is the
guard that stops a frontend file from re-growing into a monolith one pasted
block at a time.

Allowed: <script ... src="..."></script> (external module/script include).

Usage:
    guard_no_inline_style_script.py [path ...]
No args -> CI mode: scans DEFAULT_PATHS with DEFAULT_EXCLUDE applied.
Explicit path -> self-test mode: exclusions are skipped, so the guard bites a
bad fixture handed to it directly. Exit 1 (and prints file:line) on any
violation, 0 if clean.
"""
import os
import re
import sys

# ---- Configuration: edit for your repo layout --------------------------------
DEFAULT_PATHS = ["backend/static", "static"]  # HTML surfaces scanned in CI mode
DEFAULT_EXCLUDE = ("ci-kit/guards/tests/bad_fixtures/", "/.git/", "__pycache__", "/vendor/")
# -------------------------------------------------------------------------------

EXTS = (".html", ".htm")

STYLE_RE = re.compile(r"<style\b", re.IGNORECASE)
SCRIPT_OPEN_RE = re.compile(r"<script\b([^>]*)>", re.IGNORECASE)
SRC_RE = re.compile(r"\bsrc\s*=", re.IGNORECASE)


def _iter_files(paths, apply_exclude):
    for p in paths:
        if os.path.isfile(p):
            if p.endswith(EXTS):
                yield p
        elif os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for name in files:
                    fp = os.path.join(root, name)
                    if not fp.endswith(EXTS):
                        continue
                    if apply_exclude and any(x in fp for x in DEFAULT_EXCLUDE):
                        continue
                    yield fp


def _lineno(text, pos):
    return text.count("\n", 0, pos) + 1


def check_file(fp):
    problems = []
    try:
        with open(fp, encoding="utf-8") as f:
            text = f.read()
    except (UnicodeDecodeError, FileNotFoundError):
        return problems
    for m in STYLE_RE.finditer(text):
        problems.append((fp, _lineno(text, m.start()), "inline <style>: move CSS to the shared stylesheet"))
    for m in SCRIPT_OPEN_RE.finditer(text):
        if SRC_RE.search(m.group(1)):
            continue  # external include, allowed
        problems.append((fp, _lineno(text, m.start()), "inline <script>: use an ES module under your components directory"))
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
    if fail:
        print("guard_no_inline_style_script: FAILED")
    else:
        print("guard_no_inline_style_script: clean")
    return fail


if __name__ == "__main__":
    sys.exit(main(sys.argv))
