# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-11-26 UTC by Claude Code
Checkpoint status: partly verified (PR states checked 2026-11-26; "Carried over" items were not re-checked)
Owning repository: `The-825/breadcrumbs`
Source revisions: `origin/main` after PR #207 (merged 2026-11-26)

## Recovery pointer

- Owning record: PR #208 (`claude/readme-plain-terms`), the README and banner rewrite in
  plain terms (D-81).
- Next action: it touches `assets/`, so it waits for the owner ship-it label after checks
  pass. If it is still open, merge `origin/main` into the branch before labeling.

## Current state

- Open PRs at last check: #208 (this one), #206 (handoff packet template), #205 (draft,
  ignore agent-local settings and `.env` files). #205 and #206 are not mine; do not push
  to them.
- The front page now opens with a "Use it now" block (D-80, #207). #208 removes the
  airport framing from the README and banner. The essays under `docs/`
  (`the-airport-model.md`, `floating-memory.md`, the white paper and others) and the
  essay name in `kit.json` still use it and need their own pass.
- Research and repository catalog ownership moved to `The-825/staletoast` (D-67).
  The research files under `docs/` are a read-only archive.

## What just landed

- 2026-11-26: "Use it now" README block, #207 (D-80).
- 2026-11-24: first-run docs #200, checkpoint team as adopter config #202 (D-78),
  security policy #203 (D-79), archive separated in the docs index #204.
- 2026-11-10: CI enforces what the manifest claims, #198 (D-76).

## Next steps (in order)

1. Ship #208 once checks pass and the label is applied.
2. Decide whether the `docs/` essays and the `kit.json` essay name get the same
   plain-terms rewrite as the README.
3. Carried over from the 2026-11-10 refresh, not re-checked: `CLAUDE.md` may still be at
   its 220 line budget with a repo map that omits `site/`, `scripts/`, `planning/` and
   `assets/`; `templates/memory-desk/gardener/promote.py` has no test; the memory desk
   states Python 3.8+ while CI checks 3.9 and 3.11; open issues #148, #106, #110, #80 and
   #82 may be resolved, and #154, #164, #117 and #99 belong to StaleToast; issue #185
   preserves four `claude/*` heads, so confirm with the maintainer before deleting any
   remote branch.

## Carried forward, not re-verified this refresh

These came from the 2026-09-11 handoff. Confirm each before acting on it.

- Run the evaluation template in an owning system before promoting any
  work-allocation or multi-agent capability into a shipped claim.
- Keep the first repository self-assessment private until independent review and
  a specific publication approval exist.
- The Atlas independent rerun waits on the maintainer. Keep the 2026-08-12
  self-audit pinned as historical evidence.
- Research follow-ups (full-text appraisal, code traces, memory exam extensions)
  now belong to StaleToast. Do not start them in this checkout.

## Pending decisions

- `docs/figure-citation.md` is pattern-only: build its checker, or leave it labeled.
- Issue #39 dockets the codebase-flywheel port for the next standing-agents expansion.
