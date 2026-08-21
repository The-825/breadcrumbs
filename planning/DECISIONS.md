# DECISIONS.md · decisions ledger

One entry per durable ruling, newest last. Append the entry the SAME turn the
ruling lands, before moving on to the work it unblocks. Superseded entries stay
in the ledger with a "Superseded by D-<n>" line added. Never silently rewrite
an entry.

This repo teaches the pattern in [`templates/DECISIONS_TEMPLATE.md`](../templates/DECISIONS_TEMPLATE.md)
and now runs it on itself. It should have from commit one.

## D-1 · 2026-08-06 · This repo runs its own memory pattern

Ruling: `breadcrumbs` keeps a `SESSION_STATE.md` handoff at repo root and this
decisions ledger, both built from its own templates, and its `CLAUDE.md` names
the known-issues ledger it uses.
Why: a continuity sweep found that the repo teaching cue-placement memory had
none of it, so a fresh session here booted blind. Publishing a pattern you do
not run on yourself is the cheapest kind of drift and the easiest to catch.
Source: cross-repo continuity sweep, 2026-08-06 session.

## D-2 · 2026-08-06 · Book references are pointers, never summaries

Ruling: public docs may point at *From Archivist to Architect* by title in one
line. They may not summarize its content, describe what a chapter argues, or
promote an unpublished later book by title and premise.
Why: `docs/the-airport-model.md` had grown a two paragraph summary of Book 1
and Book 2 including a retired series arc, which is book content sitting in a
public repo and stale on top of it. The pointer-only convention already existed
and needed a place where it binds.
Source: cross-repo continuity sweep, 2026-08-06 session.

## D-3 · 2026-08-06 · Unbuilt tooling is named as unbuilt

Ruling: no doc in this repo describes a script, check, or CI step as existing
unless it exists in the tree. Planned work is written as planned, with the
consequence of it being absent stated plainly.
Why: `skills/adoption-verifier.md` asserted that a `doctor` script "is" in the
CI kit and "runs on every PR." Neither was true, and the same paragraph
contradicted itself by calling it a roadmap item. A public kit that overstates
its own coverage is the one defect readers cannot verify around.
Source: cross-repo continuity sweep, 2026-08-06 session.

## D-4 · 2026-08-06 · The predecessor repo is private and archived; breadcrumbs is the only public companion

Ruling: `agent-ops-playbook` has been made private and archived. `The-825/breadcrumbs`
is the sole public companion repo, and every reader-facing pointer resolves here.
Why: two public repos carried near-duplicate copies of the kit and told different
stories, one of them still pitching the book in a way this repo deliberately does not.
A continuity sweep flagged it as the largest open item on the public surface. Archived
rather than deleted, so the history survives and the decision is reversible.
Source: Jovan, session 2026-08-06.

## D-5 · 2026-08-06 · Silent about provenance, plain about the artifact

Ruling: public commit messages, PR bodies, and docs in this repo never reference the
private origin of anything here. No employer, no client, no private repo, no book, no
business strategy, and no narration of a scrub ("de-identified", "removed the internal
example", "generalized from"). Technical defects in the kit itself ARE described plainly:
a fix says what was wrong and what now holds.
Why: the two halves are often confused and they pull in opposite directions. Not
publishing your private context is ordinary discretion. Concealing a defect in a public
kit is not, and it would cost more than it saves here, because this repo's whole argument
is that a system which catches itself and keeps the evidence beats one that claims never
to be wrong. The white paper's case study IS an admitted failure, and it is the most
persuasive thing in it. A history that never admits one would sit oddly beside it, and a
reader who later finds a papered-over defect loses the one claim the kit cannot prove any
other way. D-3 already rules that unbuilt things are named as unbuilt; this is the same
principle applied to history rather than to features.
Source: Jovan, session 2026-08-06, answering the (a)/(b) question directly with "a".

## D-6 · 2026-08-06 · The guard ships, the wordlist does not

Ruling: `ci-kit/guards/guard_no_provenance_leak.py` enforces D-5. The forbidden-term list
is local and gitignored (`.provenance-terms`); the repo ships only
`provenance-terms.example` with placeholder names.
Why: a public guard containing the literal list of names you are keeping out of public
view is a leak with extra steps, and precisely the mistake the guard exists to prevent.
The scrub-narration patterns are safe to ship because they name the ACT rather than the
subject. The general form is worth stating: ship the check, keep the sensitive parameter
out of the artifact.
Source: session 2026-08-06, design constraint found while writing the guard.
## D-7 · 2026-08-06 · Commits and PRs here carry the flight metaphor

Ruling: public-facing writing in this repo, including commit messages and PR titles and
bodies, keeps a light aviation or flight reference where one fits naturally. The repo
already runs on the airport and wayfinding model: signage that tells you the next hop
rather than the whole map. The history should sound like it belongs to the same building.
Why: theme consistency is a credibility signal on a public repo, and it costs nothing when
the metaphor is already load-bearing in the docs. Light is the operative word. One
image per message, chosen because it actually describes the mechanism, never a pun
stapled to the front of a technical sentence. If the metaphor does not fit the change,
skip it rather than force it.

## D-8 · 2026-08-06 · Memory measurement ships as a doc first, tooling later

Ruling: the retrieval-measurement layer (reachability exam, injection-lane probe,
use-stamp readout, search-miss ledger) enters this repo as a pattern essay plus a ledger
schema, not as a runnable checker. A generalized reachability script has to replay the
adopter's own matcher against the adopter's own tree, so a copy of one repo's version
would be a demo rather than a tool.
Why: the concept transfers cleanly and is what readers are missing; the implementation
does not transfer without knowing the reader's boot path. Naming that boundary is
honest, and it keeps the repo's no-unbuilt-claims rule intact.
Source: session 2026-08-06.
Superseded by D-9.

## D-9 · 2026-08-06 · The retrieval exam ships runnable after all

Ruling: D-8 is reversed. `templates/ledger-tools/retrieval_exam.py` ships as a working,
self-tested checker covering reachability, the injection-lane probe, and the use-stamp
readout, with a ratchetable baseline. The matcher stays configurable rather than read
from the adopter's hook, and the script says so in its own header.
Why: D-8 treated "cannot read your hook" as a reason not to ship, which leaves the reader
with an essay and no way to act on it. The matcher shape is common enough to model and
correct with a small config, and a tool that names its own assumption is more useful than
a doc that names the same assumption and stops. The operator asked for something people
can run.
Source: Jovan, session 2026-08-06.

## D-10 · 2026-08-06 · D-5 wins over the old rule 1 wording; war stories say what a thing is

Ruling: where D-5 (never narrate a removal) and the original rule 1 wording ("anonymized
war stories are fine and are labeled as such") conflicted, D-5 wins. Rule 1 is rewritten:
war stories stay welcome and are told as what the artifact IS, never as an account of
what was taken out to publish it. Three surfaces were corrected to match: the README
landing page, this rules file, and docs/memory-measurement.md.
Why: the two rules were both live after #13 merged and they contradicted, since the label
rule 1 demanded was the exact phrasing D-5 forbids. Announcing a removal tells a reader
there was something private to remove, which is the disclosure the removal was meant to
prevent, so the label defeats its own purpose. The guard already encoded D-5's side.
Source: Jovan, session 2026-08-06.

## D-11 · 2026-08-08 · The memory desk ships as the read-side refinement

Ruling: retrieval gets one mechanical door, `templates/memory-desk/`: a flat,
tool-queried fact index with a raw-capture journal, a scheduled gardener contract, and
a push-hook trio, designed so the lightest model tier on lowest effort navigates by
exact match instead of judgment. Catalog routing stays right for essay-shaped corpora;
the desk fronts it, and the two docs cross-reference rather than compete.
Why: the operator asked what a refined version of this memory system would look like,
and the honest answer is that weak sessions fail at retrieval judgment, not execution,
so judgment moves out of the session and into the index's maintenance loop.
Source: operator request, session 2026-08-08.

## D-12 · 2026-08-09 · Tiered merge gate
Ruling: The approval label gates by diff, not blanket. Safe set (docs/, checklists/, README.md, planning/DECISIONS.md, additive or modified only) merges on green unlabeled; deletions, renames, workflows, guards, templates, skills, kit.json, llms.txt, CLAUDE.md, and everything else keep the label. Policy lives in ci-kit/workflows/greenlight_tiers.py; the gate runs the base branch's copy.
Why: A blanket label past a few PRs a day becomes a batch rubber stamp that still looks like review; tiering keeps the human where a miss costs something.
Source: Operator directive, session 2026-08-09 ("automate the merge gate and place the human review at a more intentional component").

## D-13 · 2026-08-09 · SESSION_STATE.md joins the tier safe set
Ruling: Checkpoint refreshes of SESSION_STATE.md merge on green with no label (modification/addition only; deleting it still gates).
Why: The handoff refresh is routine, reviewed by its own next reader, and blocking it on the label defeats the checkpoint cadence.
Source: Operator directive, session 2026-08-09.

## D-14 · 2026-08-19 · The axis is auditable memory, not remembering at all
Ruling: The whitepaper's framing sharpens from "agents forget between sessions" to
"the question is whether what they remember is inspectable." Consumer assistants now
ship cross-session memory by default; the differentiator is not recall but whether a
stored fact can be read, dated, and verifiably corrected. Section 6 carries the
contrast plus a three-test rubric readers can apply to any memory system, this one
included, and states plainly that the automatic approach is the right choice for a
reader whose problem is convenience.
Why: The old framing was becoming false as products shipped memory, and it undersold
the actual claim. Prompted by a first-party observation: an assistant asked to describe
its own memory reported summarized impressions it could not show, diff, or date.
Source: session 2026-08-19, operator-run probe of a consumer assistant's self-description

## D-15 · 2026-08-19 · The axis is governed memory · amends D-14

Ruling: the positioning axis sharpens once more, from auditable memory to **governed**
memory. Inspectable storage is the floor; governance is the claim. D-14 was right that
recall is no longer the differentiator and wrong about what replaced it: it named the
property that a git-backed store gives you for free, which several products now ship.

Why: Letta shipped Context Repositories on 2026-02-12, storing a coding agent's context
as files that are "git-backed, so every change to memory is automatically versioned with
informative commit messages." Memoria and GitAgent occupy the same ground in open source.
So "you can read it and date it" is no longer a position, it is table stakes, and D-14
staked the paper on it the same week.

What survives is narrower and was already in the paper's body: write-time refusal,
verification gated on a named oracle rather than the writer's confidence, obligation
tracking, versioned staleness, and append-only supersession. Versioning answers what
changed. Governance answers who was allowed to write it, what had to be true first, and
whether a correction actually landed. A perfectly versioned memory can be confidently,
durably wrong, and the commit log will faithfully record every step of it being wrong.

Section 6 already argued this; only the headline was behind. Whitepaper goes to 1.3,
names Letta directly where it already disclaimed the git substrate, and adds the
storage-versus-process distinction to the three-test rubric.

Source: Jovan, 2026-08-19, on a market check that verified the Letta page directly.
Analysis in the BetterMe repo, `825/agent-ops-lane-v1.md`, and logged there as AL-8.

## D-16 · 2026-08-20 · D-3 gets a mechanical check and a stated default

Ruling: D-3 stands and gains two things. Where a doc claims a check exists, the
check gets built rather than the claim softened, when building it is cheap
(`docs/context-budget.md` claimed a budget guard; the guard now ships as
`ci-kit/guards/guard_context_budget.py` with `CONTEXT_BUDGET.md` as this repo's
real manifest). And every doc describing a mechanism now states, in its own
header, whether that mechanism ships here. Pattern-only is a fine answer; silence
is not, because a reader defaults to assuming it ships.
Why: an audit against the whole docs tree found one flat D-3 violation and seven
docs that made no false claim but never said which side of the line they were on.
The kit's own best examples (`floating-memory.md`, `cue-placement-ladder.md`) had
the label; the rest just never got it, which means the rule was being followed by
habit rather than by contract.
Source: claim-to-code audit of the docs tree, 2026-08-20, and the branch
`claude/context-budget-guard`.

## D-17 · 2026-08-20 · Borrow mechanisms, not a memory platform

Ruling: the runnable memory engine adds two focused mechanisms from the wider
agent-memory field: facts may cite the exact source episodes that produced them,
and episodic recall fuses lexical, action/tag, and recency rankings with reciprocal
rank fusion. The kit does not adopt an external database, autonomous memory
rewriting, or unverified agent-generated facts.
Why: the engine already ships bi-temporal replay, scoped assembly, oracle-gated
verification, supersession, and tombstones. Replacing that contract would add a
platform while weakening the governance distinction; provenance-linked writes and
deterministic fusion close real gaps without changing the storage model.
Source: operator-approved GitHub memory-system benchmark, 2026-08-20.

## D-18 � 2026-08-21 � Contradictions are proposals before they are mutations

Ruling: the runnable memory engine classifies normalized exact matches and
fully bounded non-overlapping validity windows deterministically, then returns
a typed review-only proposal for semantic conflicts. Missing, malformed, or
failed evaluator output remains unknown; it never becomes compatible by
default, and the proposal path never mutates facts or tombstones.
Why: contradiction resolution can improve correction quality only if a failed
probe cannot erase evidence or quietly authorize a write.
Source: operator-approved GitHub memory-system audit, 2026-08-21.

