---
description: Refresh SESSION_STATE.md, the living handoff file, on the operator's "checkpoint" trigger. Repopulates branch, in-flight work, next steps, and pending decisions; preserves the irreplaceable-values section verbatim.
argument-hint: "[optional note, e.g. 'mid-refactor', folded into current state]"
allowed-tools: Bash, Grep, Read, Edit, Write
---

Refresh `SESSION_STATE.md` so the next session picks up mid-flight instead of trusting a lossy summary. This fires on the operator's **"checkpoint"** trigger (or "update state" / "save where we are"). The whole point of this command is to EDIT `SESSION_STATE.md`, so do that as the action.

The file follows the session-state template (see `templates/SESSION_STATE_TEMPLATE.md` in the companion repo, or your repo's copy of it): current state, next steps, pending decisions, standing instructions, irreplaceable exact values, recently landed.

## Step 1: Gather current reality

1. Open PRs: `gh pr list --state open --limit 20`
2. Current branch: `git branch --show-current`
3. Working tree (uncommitted, in-flight edits): `git status -s`
4. Commits ahead of the base: `git log --oneline origin/<main-branch>..HEAD 2>/dev/null | head -10`
5. Last 5 merges: `git log --oneline --merges -5`

## Step 2: Rewrite against reality

Read the current `SESSION_STATE.md`. Repopulate these sections from Step 1 plus what this session knows, REPLACING stale content rather than appending:

- **Current state:** last-refreshed date, active branch, open PR numbers (or "none"), and the in-flight uncommitted edits as `file path: what is half-done in it`, one line each. Fold in `$ARGUMENTS` if given.
- **Next steps:** the concrete next actions, in order, each specific enough to execute cold.
- **Pending decisions:** anything parked on the operator's input, phrased so a yes/no or a pointer unblocks it.
- **Recently landed:** trim to the last handful; move anything genuinely done out to the changelog and delete it here.

## Step 3: Preserve the irreplaceable-values section verbatim

That section is the reserve for exact values that cannot be re-derived from the repo: in-flight PR numbers, file:line references, figures the operator corrected in-session, IDs, one-off command outputs. **Never trim or paraphrase it.** Add newly-surfaced exact values if this session produced any; otherwise leave it untouched. A compaction or summary must carry this section word for word, and keeping it in one named place is what makes that instruction enforceable.

## Step 4: Discipline

- Keep every entry terse. This file is a handoff, NOT a changelog and NOT the priority list.
- Do not duplicate what `<roadmap-file>` already tracks; note only the slice being actively touched.
- Move truly-done items out. `SESSION_STATE.md` must never grow into a log; a stale or bloated handoff is worse than none, because the next session will trust it.

## Step 5: Write it

Apply the edits to `SESSION_STATE.md`. This is a doc refresh: no commit, no push, no PR, unless the operator asks. End with a one-line confirmation of what changed in the handoff.
