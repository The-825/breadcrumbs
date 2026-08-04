#!/usr/bin/env bash
# PreCompact hook: save the full conversation transcript before compaction.
#
# Compaction rewrites the conversation into a summary, and detail gets
# lost. This hook fires before every compaction (manual and automatic)
# and copies the complete transcript JSONL to a local save directory, so
# the post-compaction session can grep the raw history instead of
# re-deriving or guessing. The companion SessionStart hook
# (post-compact-pointer.sh, matcher "compact") tells the model where the
# save landed.
#
# Saves live OUTSIDE the repo on purpose. A transcript can contain
# anything the session touched (credentials, live records, private
# data), so it must never be committed or pushed. Saves are for
# within-container recovery, not archival; your curated handoff file
# stays the durable layer.
#
# Input (stdin JSON): {session_id, transcript_path, trigger, ...}
# Output: one {"systemMessage": ...} line so the save is visible.
# Fails open: any problem exits 0 rather than blocking the compaction.

payload=$(cat)

SAVE_DIR="${COMPACT_SAVE_DIR:-$HOME/.claude/compaction-saves}"
mkdir -p "$SAVE_DIR" 2>/dev/null || exit 0

if command -v jq >/dev/null 2>&1; then
  transcript=$(printf '%s' "$payload" | jq -r '.transcript_path // empty' 2>/dev/null)
  trigger=$(printf '%s' "$payload" | jq -r '.trigger // "auto"' 2>/dev/null)
  session=$(printf '%s' "$payload" | jq -r '(.session_id // "session") | .[0:12]' 2>/dev/null)
else
  # No jq: best-effort sed extraction of the one field that matters.
  transcript=$(printf '%s' "$payload" | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
  trigger=auto
  session=session
fi

[ -n "$transcript" ] && [ -f "$transcript" ] || exit 0
[ -n "$trigger" ] || trigger=auto
[ -n "$session" ] || session=session

ts=$(date +%Y%m%d-%H%M%S)
dest="$SAVE_DIR/${session}-${ts}-${trigger}.jsonl"
cp "$transcript" "$dest" 2>/dev/null || exit 0
printf '%s\n' "$dest" > "$SAVE_DIR/LATEST"

# Retention: keep the 20 newest saves. A long session can compact many
# times, and unbounded copies of a large transcript bloat the container.
ls -1t "$SAVE_DIR"/*.jsonl 2>/dev/null | tail -n +21 | while IFS= read -r old; do
  rm -f -- "$old"
done

printf '{"systemMessage": "Pre-compaction transcript saved: %s"}\n' "$dest"
