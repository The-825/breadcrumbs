# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-08-21 (governed learning cycle in progress)

## Current state

- Active branch: `claude/governed-learning-cycle`.
- In-flight edits: sourced knowledge, application or teach-back, evaluated
  understanding, novel-context transfer, and review-only mastery proposals.
- Everything through PR #78 is merged on `main`.

## What just landed

**Governed replay proposals (D-23).** Offline replay can surface patterns
without turning its own synthesis into truth or permission.

## Next steps / watch

- Run the replay selftest and full repository gates, inspect the diff, then
  publish and greenlight under the operator's standing instruction.
- Atlas follow-up: the operator will contact Simon for an independent rerun.
  Keep the 2026-08-12 self-audit pinned as historical evidence rather than
  silently rewriting it to match current main.
- `docs/figure-citation.md` is now labeled pattern-only. Building its checker
  remains a separate feature decision, not documentation cleanup.
- Issue #39 dockets the codebase-flywheel port (trigger: standing-agents
  expansion). The issue ledger also holds the synthetic-fixtures limitation.

## Pending decisions

- The figure-citation checker: build or label. See above.
- D-22 is the latest ruling (2026-08-21, trust promotion has an authority
  ceiling).
