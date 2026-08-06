# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-08-06

## Current state

- Active branch: `claude/archive-audit-findings`
- Open PR: none at the time of writing. PR #9 (specification debt, three more
  data truth rules, multi-agent lessons) merged 2026-08-06.
- In-flight, uncommitted edits: none. See "What just landed" below.

## What just landed

An audit of eighteen months of the operator's own session archive, mined for
where the memory system failed, then landed as repo content rather than left in
chat. Three new docs, one whitepaper section, and a set of continuity fixes.

- `docs/specification-debt.md`, `docs/artifact-correction-ledger.md`, and
  `docs/batched-decision-blocks.md` are new. The third is the unusual one: it
  is a positive finding, a structure that made sessions go well, with real
  counts behind it.
- `docs/breadcrumbs-whitepaper.md` gained section 4.5, the archive audit, with
  the counts and an explicit statement of what that evidence does and does not
  establish.
- `docs/enforcement-manifest.md` gained the document output contract.
- Continuity fixes: the book reference in `docs/the-airport-model.md` cut back
  to a pointer, the unbuilt `doctor` script in `skills/adoption-verifier.md`
  named as unbuilt, and `docs/README.md` brought current.

## Next steps

1. Decide what happens to the retired `agent-ops-playbook` repo. It is still
   public and still carries a near-duplicate of this kit plus a book pitch this
   repo deliberately does not have. Two public repos telling different stories
   is the single largest open item. Recommendation: archive it on GitHub with a
   README pointer here, which is reversible. This needs the operator's call.
2. Name a known-issues ledger for this repo in `CLAUDE.md` and start it.
3. The `doctor` script from `skills/adoption-verifier.md` is still unbuilt.

## Pending decisions

- The retired public repo, above.
- Whether the airport and caught-itself framing that anchors this repo's public
  narrative should also appear in the book, which currently does not use it.
  Deliberate split or drift, the operator's call either way.
