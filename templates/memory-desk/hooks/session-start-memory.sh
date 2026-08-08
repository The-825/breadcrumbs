#!/usr/bin/env bash
# SessionStart hook: put the memory desk in context at the door.
#
# Stdout on this event becomes model context, so a booting session gets the
# kernel (MEMORY.md), the last few journal lines, and the one lookup move
# before its first turn. The session does not go looking; the environment
# says it at the door. Silent when the desk is absent, fail-open everywhere:
# a broken hook must never block a boot.
#
# Assumes the desk was copied to memory/ at the repo root; override with
# MEMORY_DESK_DIR if you put it elsewhere.

root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -z "$root" ] && exit 0
desk="${MEMORY_DESK_DIR:-$root/memory}"
kernel="$desk/MEMORY.md"
[ -f "$kernel" ] || kernel="$desk/MEMORY_TEMPLATE.md"
[ -f "$kernel" ] || exit 0

cat "$kernel"

if [ -f "$desk/journal.jsonl" ]; then
  echo ""
  echo "last journal entries (raw capture; the gardener curates weekly):"
  tail -n 3 "$desk/journal.jsonl"
fi

if [ -f "$desk/index.tsv" ]; then
  rows=$(grep -Ecv '^[[:space:]]*(#|$)' "$desk/index.tsv" 2>/dev/null || echo "?")
  echo ""
  echo "index: $rows rows. every factual lookup starts with: memory/mem <words>"
fi
exit 0
