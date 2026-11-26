# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-11-26 UTC by Claude Code
Checkpoint status: partly verified (PR states checked 2026-11-26; "Carried over" items were not re-checked)
Owning repository: `The-825/breadcrumbs`
Source revisions: `origin/main` `1342747` (PR #208)

## Recovery pointer

- Owning record: the PR from `claude/docs-plain-terms` (D-82), the kit essays in plain
  terms.
- Next action: it renames a docs file and edits `kit.json`, so it waits for the owner
  ship-it label after checks pass. If it is still open, merge `origin/main` into the
  branch before labeling.

## Current state

- Open PRs at last check: this one (`claude/docs-plain-terms`, D-82), #206 (handoff packet
  template) and #205 (draft, ignore agent-local settings and `.env` files). #205 and #206
  are not mine; do not push to them.
- The front page opens with a "Use it now" block (D-80, #207) and no longer uses the
  airport framing (D-81, #208). D-82 carries that through the kit essays:
  `the-airport-model.md` is now `pointers-and-trails.md`, and the white paper (still
  Version 1.5, with a dated revision note), `floating-memory.md` and the smaller essays
  say the same things in plain terms. The research archive under `docs/` and older ledger
  entries keep the old wording on purpose.
- Research and repository catalog ownership moved to `The-825/staletoast` (D-67).
  The research files under `docs/` are a read-only archive.

## What just landed

- 2026-11-26: plain-terms README and banner, #208 (D-81). "Use it now" README block, #207 (D-80).
- 2026-11-24: first-run docs #200, checkpoint team as adopter config #202 (D-78),
  security policy #203 (D-79), archive separated in the docs index #204.
- 2026-11-10: CI enforces what the manifest claims, #198 (D-76).

## Next steps (in order)

1. Ship the D-82 PR once checks pass and the label is applied. The old essay URL
   `docs/the-airport-model.md` no longer exists; update any outside link to
   `docs/pointers-and-trails.md`.
2. Carried over from the 2026-11-10 refresh, not re-checked: `CLAUDE.md` may still be at
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
