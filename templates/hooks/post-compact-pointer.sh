#!/usr/bin/env bash
# SessionStart hook, matcher "compact": fires right after a compaction.
#
# Stdout on this event is added to the model's context, so this is how
# the post-compaction session learns that the full pre-compaction
# transcript was saved (by pre-compact-save.sh) and where it is. Silent
# when no save exists. Register it with the "compact" matcher so it
# speaks only after compaction, not on every session start.

SAVE_DIR="${COMPACT_SAVE_DIR:-$HOME/.claude/compaction-saves}"
latest=""
[ -f "$SAVE_DIR/LATEST" ] && latest=$(cat "$SAVE_DIR/LATEST" 2>/dev/null)

if [ -n "$latest" ] && [ -f "$latest" ]; then
  cat <<EOF
Context was just compacted. The full pre-compaction transcript (JSONL) is saved at: $latest
If a detail feels missing from the summary (a decision, a figure, a path, an in-flight edit), grep that file before re-deriving or guessing. Older saves: $SAVE_DIR.
Repo files stay the source of truth for anything the summary paraphrases; trust them over the summary wherever they disagree.
EOF
fi
