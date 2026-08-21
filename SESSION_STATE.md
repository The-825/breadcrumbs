# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-08-21 (Breadcrumb Score in progress)

## Current state

- Active branch: `claude/breadcrumb-score`.
- In-flight edits: versioned evidence assessment, deterministic coverage and
  readiness scoring, public-ready refusal rules, and focused tests.
- Everything through PR #79 is merged on `main`.

## What just landed

**Governed learning cycle (D-25).** Learning requires sourced knowledge,
application, independent evaluation, and novel-context transfer before mastery
may be proposed.

## Next steps / watch

- Run the Breadcrumb Score selftest and full repository gates, inspect the
  diff, then publish the feature PR for operator review.
- The first repository self-assessment remains separate until the evaluator
  itself is green.
- Atlas follow-up: the operator will contact Simon for an independent rerun.
  Keep the 2026-08-12 self-audit pinned as historical evidence rather than
  silently rewriting it to match current main.
- `docs/figure-citation.md` is labeled pattern-only. Building its checker
  remains a separate feature decision.
- Issue #39 dockets the codebase-flywheel port. The issue ledger also holds the
  synthetic-fixtures limitation.

## Pending decisions

- The figure-citation checker: build or label. See above.
- D-26 is the latest ruling (2026-08-21, readiness separates evidence coverage
  from score).
