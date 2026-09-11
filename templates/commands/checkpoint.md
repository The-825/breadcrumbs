---
description: Refresh SESSION_STATE.md from current, source-linked evidence while preserving irreplaceable values and superseded history.
argument-hint: "[optional note, e.g. 'mid-refactor', folded into current state]"
allowed-tools: Bash, Grep, Read, Edit, Write
---

Refresh `SESSION_STATE.md` so the next session picks up mid-flight instead of trusting a lossy summary. This fires on the operator's **"checkpoint"** trigger (or "update state" / "save where we are"). The whole point of this command is to EDIT `SESSION_STATE.md`, so do that as the action.

The file follows the session-state template (see `templates/SESSION_STATE_TEMPLATE.md` in the companion repo, or your repo's copy of it): current state, next steps, pending decisions, standing instructions, irreplaceable exact values, recently landed.

## Step 1: Gather current reality

1. Confirm the bounded working directory and repository identity.
2. Current branch, HEAD, base revision, and working tree.
3. Open PR, current PR head, checks, review, and merge state. If the head changed,
   invalidate checks recorded for an older head.
4. Commits ahead of the base and only the recent merges needed to resolve state.
5. Sources and assumptions used by in-flight decisions. Mark unavailable evidence
   unknown instead of filling it from memory.

## Step 2: Rewrite against reality

Read the current `SESSION_STATE.md`. Repopulate these sections from Step 1 plus what this session knows, REPLACING stale content rather than appending:

- **Current state:** observed time, verification status, owning repository and
  directory, source revisions, branch, open PR, current-head checks and review,
  merge, deployment, and in-flight edits. Keep deployment separate from merge.
- **Next steps:** the concrete next actions, in order, each specific enough to execute cold.
- **Pending decisions:** anything parked on the operator's input, phrased so a yes/no or a pointer unblocks it.
- **Decisions, corrections, and supersession:** cite the source and name the prior
  claim superseded. Do not erase history.
- **Failures and workarounds:** record the action, observation, known versus
  suspected cause, side effects, blocker, next action, workaround rationale,
  checks, and residual limits. Attempted recovery is not verified recovery.
- **Assumptions and evidence validity:** say what source or assumption change
  invalidates reused evidence.
- **Unfinished work:** keep its owner, state, next action, and needed proof visible.
- **Recently landed:** trim to the last handful; move anything genuinely done out to the changelog and delete it here.

## Step 3: Preserve the irreplaceable-values section verbatim

That section is the reserve for exact values that cannot be re-derived from the repo: in-flight PR numbers, file:line references, figures the operator corrected in-session, IDs, one-off command outputs. **Never trim or paraphrase it.** Add newly-surfaced exact values if this session produced any; otherwise leave it untouched. A compaction or summary must carry this section word for word, and keeping it in one named place is what makes that instruction enforceable.

## Step 4: Discipline

- Keep every entry terse. This file is a handoff, NOT a changelog and NOT the priority list.
- A completed milestone does not complete its parent task automatically.
- Old memory supplies context, not new authority.
- Record a runtime receipt only when the runtime returned one. Markdown does not
  prove that a hook or external action ran.
- Do not duplicate what `<roadmap-file>` already tracks; note only the slice being actively touched.
- Move truly-done items out. `SESSION_STATE.md` must never grow into a log; a stale or bloated handoff is worse than none, because the next session will trust it.

## Step 5: Write it

Apply the edits to `SESSION_STATE.md`. Follow the repository's current authority
and release rules. Do not infer new authority from this command. End with a one-line
confirmation of what changed in the handoff.
