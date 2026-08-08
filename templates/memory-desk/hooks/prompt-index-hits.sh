#!/usr/bin/env bash
# UserPromptSubmit hook: run the incoming prompt through the memory index and
# inject the matching rows into the turn's context.
#
# This is the push half of the desk: the answer arrives before the model
# thinks to look, which is the only retrieval that works on a session that
# never learned to look. mem's --stdin mode is its quiet hook form: it prints
# hits (capped, higher match floor) or nothing, so a prompt with no index
# overlap injects zero lines and ordinary conversation stays noise-free.
#
# Fail-open on every path: a broken hook must never block a prompt. Assumes
# the desk at memory/; override with MEMORY_DESK_DIR.

prompt="$(jq -r '.prompt // ""' 2>/dev/null)"
[ -z "$prompt" ] && exit 0

root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -z "$root" ] && exit 0
mem="${MEMORY_DESK_DIR:-$root/memory}/mem"
[ -f "$mem" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

if hits="$(printf '%s' "$prompt" | python3 "$mem" --stdin 2>/dev/null)"; then
  [ -z "$hits" ] && exit 0
  echo "[memory-desk] index rows matching this prompt (more: memory/mem <words>):"
  echo "$hits"
fi
exit 0
