# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-08-26 (collaborative-intelligence research checkpoint)

## Current state

- Active branch: `claude/collaborative-intelligence-research-system`, cut from
  `origin/main` at `967b905`.
- Merged in PR #86: a host-bound context service derives memory clearance from
  an authenticated principal and fixed policy. Requests cannot assert or widen
  audience, and ungranted principals fail closed.
- The low-level memory engine, golden exam, and new scope-gate selftest pass.

## In flight

**Collaborative-intelligence research method (D-29).** The four-source checkpoint is
packaged as one public, evidence-honest ledger with a shared method, corroboration
matrix, dependency map, research debt, and ranked questions. Paper 002 is identified
as the Fügener, Walzner, and Gupta task-allocation study; the earlier conversational
reference to Raisch and Krakowski was a related citation, not the reviewed source.
Validation is complete; commit, PR, and merge remain.

## What just landed

**A2A score export and work-governance related work (D-27).** Both are merged on
`main`. Breadcrumb Score remains evidence-scoped and publication-gated.

## Next steps / watch

- Seek negative evidence before adding a fifth supportive source. Do not promote the
  candidate work-allocation capability into a shipped claim without a bounded test in
  consequential, privacy-constrained work.
- Request an independent Atlas rerun when the maintainer is ready to contact Simon.
- Keep the first repository self-assessment private until independent review
  and a specific publication approval exist.
- Atlas follow-up: contact Simon for an independent rerun only after the scope
  gate is merged and publicly inspectable.
  Keep the 2026-08-12 self-audit pinned as historical evidence rather than
  silently rewriting it to match current main.
- `docs/figure-citation.md` is labeled pattern-only. Building its checker
  remains a separate feature decision.
- Issue #39 dockets the codebase-flywheel port. The issue ledger also holds the
  synthetic-fixtures limitation.

## Pending decisions

- The figure-citation checker: build or label. See above.
- D-28 is the latest ruling (2026-08-24, scope is derived from trusted
  identity).
