#!/usr/bin/env bash
# PreToolUse gate: screen non-git outbound tool calls for PII-shaped tokens
# before they leave the building. Covers the lane git hooks do not: an
# email draft, a cloud-drive upload, an artifact/publish call. Runs the
# SAME detector CI and a pre-push git guard use
# (ci-kit/guards/guard_no_pii_in_fixtures.py --stdin), so all three call
# sites share one set of regexes instead of three copies that drift. See
# outbound-pii-screen.md for the full pattern and the pre-push wiring.
#
# Fail-OPEN by design on tooling absence (no python3, no guard script, no
# payload): blocking every outbound call on a broken screen halts
# operations, and the git lane (a pre-push git guard, call site 2 in
# outbound-pii-screen.md) keeps its own independent gate. A block here is always a real finding, never an
# infrastructure error.
set -u

payload="$(cat 2>/dev/null || true)"
[ -z "$payload" ] && exit 0

root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"
guard="$root/ci-kit/guards/guard_no_pii_in_fixtures.py"
[ -f "$guard" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

# Pull every string out of tool_input, plus the CONTENT of any file_path /
# files[] the tool is about to publish (some outbound tool shapes pass a
# path, not a body; screening only the path string would see nothing).
text="$(printf '%s' "$payload" | python3 -c '
import json, os, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti = d.get("tool_input") or {}
out = []

def walk(v):
    if isinstance(v, str):
        out.append(v)
    elif isinstance(v, dict):
        for x in v.values():
            walk(x)
    elif isinstance(v, list):
        for x in v:
            walk(x)

walk(ti)
paths = []
fp = ti.get("file_path")
if isinstance(fp, str):
    paths.append(fp)
fl = ti.get("files")
if isinstance(fl, list):
    paths += [p for p in fl if isinstance(p, str)]
for p in paths:
    if os.path.isfile(p):
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                out.append(f.read())
        except OSError:
            pass
print("\n".join(out))
' 2>/dev/null || true)"
[ -z "$text" ] && exit 0

if findings="$(printf '%s\n' "$text" | python3 "$guard" --stdin 2>&1)"; then
  exit 0
fi

{
  echo "Outbound PII screen (outbound-pii-screen.sh): PII-shaped token detected in this outbound payload. The guard covers Gmail/Slack drafts, cloud-drive writes, and artifact/publish calls, not just git. Redact and retry:"
  printf '%s\n' "$findings" | grep -v '^guard_no_pii_in_fixtures:'
} >&2
exit 2
