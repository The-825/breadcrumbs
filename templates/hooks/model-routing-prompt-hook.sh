#!/usr/bin/env bash
# UserPromptSubmit hook: classify the incoming prompt's task shape and
# inject a one-line model-tier recommendation into the session context.
# Pairs with templates/commands/model-check.md (the on-demand version) and
# docs/model-playbook.md (the routing table); this is the automatic form,
# so the routing check fires without anyone remembering to run it.
#
# Hook input is JSON on stdin: {"prompt": "...", ...}. Extract the prompt
# with jq and pipe it to the classifier sitting next to this script.
# Fail-open on EVERY path: a broken hook must never block a prompt, and a
# silent exit is the correct output for anything unclassifiable.
prompt="$(jq -r '.prompt // ""' 2>/dev/null)"
[ -z "$prompt" ] && exit 0

root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -z "$root" ] && exit 0
script="$root/.claude/hooks/task_shape.py"
[ -f "$script" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

printf '%s' "$prompt" | python3 "$script" 2>/dev/null || true
exit 0
