#!/usr/bin/env python3
"""PostToolUse hook (matcher: Edit|Write|MultiEdit): file-scoped memory notes.

An index row scoped to a file (an alias reading file:<repo-relative-path>) is
a gotcha about that file: the invariant an edit keeps breaking, the companion
file that must change with it. This hook fires when a write first touches the
file and injects those rows as additionalContext, so the note arrives while
the edit is still cheap to correct, and never blocks the tool call.

PostToolUse rather than PreToolUse on purpose: on this harness, plain stdout
from a PreToolUse hook is not added to model context, and the JSON form that
is would also carry a permission decision, which an informational hook must
not touch. Right after the first write is close enough to steer the work.

Fail-open by design: always exits 0, stdlib only, no network. A broken hook
must never block a turn. Assumes the desk at memory/ under the repo root;
falls back to the index next to this script so the hook also works from an
uncopied templates checkout.
"""
import json
import sys
from pathlib import Path


def find_repo_root(start):
    p = start
    while p != p.parent:
        if (p / ".git").exists():
            return p
        p = p.parent
    return None


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        if not isinstance(payload, dict):
            return 0
        fp = (payload.get("tool_input") or {}).get("file_path", "")
        if not fp:
            return 0

        here = Path(__file__).resolve().parent
        root = find_repo_root(here)
        idx = None
        if root is not None and (root / "memory" / "index.tsv").exists():
            idx = root / "memory" / "index.tsv"
        elif (here.parent / "index.tsv").exists():
            idx = here.parent / "index.tsv"
        if idx is None:
            return 0

        rel = fp
        if root is not None:
            try:
                rel = str(Path(fp).resolve().relative_to(root))
            except (ValueError, OSError):
                rel = fp
        needle = f"file:{rel}".lower()

        notes = []
        for line in idx.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 5:
                continue
            aliases = [a.strip().lower() for a in parts[1].split("|")]
            if needle in aliases:
                notes.append(f"{parts[0].strip()}: {parts[2].strip()} (source: {parts[3].strip()})")
        if not notes:
            return 0

        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": f"[memory-desk] notes on {rel}: " + " · ".join(notes),
            }
        }))
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
