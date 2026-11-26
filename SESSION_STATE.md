# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-11-26 UTC by Claude Code
Checkpoint status: partly verified (PR and main state checked 2026-11-26; "Carried over" items were not re-checked)
Owning repository: `The-825/breadcrumbs`
Source revisions: `origin/main` `199be69` (PR #211)

## Recovery pointer

- Owning record: the PR from `claude/neutral-workflow-routing` (D-84), which renames the
  public workflow routing file and its key.
- Next action: it renames a file and edits `kit.json`, so it waits for the owner ship-it
  label after checks pass. If it is still open, merge `origin/main` into the branch
  before labeling.

## Current state

- Open PRs at last check: this one (`claude/neutral-workflow-routing`, D-84), #212 (intro
  clip on the home page) and #205 (draft, ignore agent-local settings and `.env` files).
  #212 and #205 are not mine; do not push to them.
- The public pages no longer name the retired coordination tool: prose went in D-83 (#211),
  and D-84 renames the data contract. `docs/jarvis-workflow-routing.json` is now
  `docs/workflow-routing.json`, the registry key `jarvis_routes` is `route_ids`, and
  route IDs `JR-001` to `JR-006` are `RT-001` to `RT-006`. Older ledger entries and the
  research archive under `docs/` keep the old names on purpose. Third-party repositories
  that happen to be named JARVIS in the research files are source names, not references to
  the retired tool.
- The front page opens with a "Use it now" block (D-80) and plain terms (D-81); the kit
  essays follow (D-82). The old essay URL `docs/the-airport-model.md` no longer exists;
  use `docs/pointers-and-trails.md`.
- Research and repository catalog ownership moved to `The-825/staletoast` (D-67).
  The research files under `docs/` are a read-only archive.

## What just landed

- 2026-11-26: coordination-tool names out of public pages, #211 (D-83). README claim about
  other vendors corrected, #210. Kit essays in plain terms, #209 (D-82). Handoff packet
  template, #206.
- 2026-11-26: plain-terms README and banner, #208 (D-81). "Use it now" README block, #207 (D-80).
- 2026-11-24: first-run docs #200, checkpoint team as adopter config #202 (D-78),
  security policy #203 (D-79), archive separated in the docs index #204.

## Next steps (in order)

1. Ship the D-84 PR once checks pass and the label is applied. Anything outside this repo
   that links to `docs/jarvis-workflow-routing.json` or reads `jarvis_routes` needs the
   new names; a search of the other portfolio repos has not been run.
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
