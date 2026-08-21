# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-08-21 (repository continuity cleanup in progress)

## Current state

- Active branch: `claude/repo-continuity-cleanup`.
- In-flight edits: align the README, machine inventory, agent map, figure-citation
  status, and this handoff with the authority-ceiling work already on main.
- Everything through PR #75 is merged on `main`.

## What just landed

**The trust authority ceiling (D-22).** Verification now names a distinct tool
or human authority. Agent repetition and self-verification cannot turn an
assertion into verified memory.

## Next steps / watch

- Run continuity checks, inspect the diff, then publish. This is a docs-only
  cleanup and should use the repository's safe merge tier.
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
