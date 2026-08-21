# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-08-21 (A2A score export in progress)

## Current state

- Active branch: `claude/a2a-score-export`.
- In-flight edits: a non-required A2A Agent Card extension that links to a
  published Breadcrumb Score assessment without exposing authenticated fields.
- Breadcrumb Score is merged on `main`.

## What just landed

**Breadcrumb Score (D-26).** Evidence coverage is separate from score, and
public-ready assessments require owner opt-in, human review, and publication approval.

## Next steps / watch

- Publish the A2A score-export feature PR after full gates and public review.
- Keep the first repository self-assessment private until independent review
  and a specific publication approval exist.
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
