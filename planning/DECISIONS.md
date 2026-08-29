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

## D-19 ? 2026-08-21 ? Negative memory guards derivation before it guards CI

Ruling: the memory-desk gardener consults rejected-value tombstones before
promoting journal entries. A normalized key-and-answer match is refused without
changing the index; the existing post-write integrity check remains a backstop,
not the first point at which re-derivation is discovered.
Why: a pass that writes a known-wrong value and then fails leaves the derived
store wrong even though the failure was reported. Forgetting is incomplete until
retained evidence cannot launder the rejected answer back into ordinary recall.
Source: operator-approved Atlas lifecycle-strengthening pass, 2026-08-21.

## D-20 ? 2026-08-21 ? Consolidation starts as a durable proposal

Ruling: possible semantic duplicates found during gardening become stable,
typed, idempotent proposal records carrying both candidate and existing
lineage. Proposal creation never merges, hides, promotes, or rewrites memory;
durable mutation still requires human review through a later explicit path.
Why: an ephemeral warning cannot support headless review, while an autonomous
rewrite can silently discard nuance or evidence. A durable proposal preserves
both the work queue and the authorization boundary.
Source: operator-approved Atlas extraction-strengthening pass, 2026-08-21.

## D-21 ? 2026-08-21 ? Retrieval quality is a committed corpus, not a demo

Ruling: the runnable memory engine gains a versioned golden-query corpus and a
stdlib-only exam wired into CI. Cases name both expected and forbidden output
across fusion, scope, learned-time replay, valid-time filtering, and trust-time
masking; repeated cases must render identically.
Why: one happy-path selftest proves a mechanism can work. A committed corpus
proves the specific failures already judged unacceptable stay fixed as ranking
and lifecycle code evolve.
Source: operator-approved Atlas retrieval-strengthening pass, 2026-08-21.

## D-22 ? 2026-08-21 ? Trust promotion has an authority ceiling

Ruling: semantic facts record the actor and authority class that asserted them.
Verification requires evidence plus a distinct verifier whose authority is a
tool or human; agent authority cannot promote a claim, and the asserting actor
cannot verify itself. Repetition and added provenance preserve an existing
trust state but never raise it.
Why: separating evidence from authority prevents an agent-generated claim from
becoming verified merely because another agent repeated it or because the same
actor attached more sources. Trust changes require an independent boundary.
Source: operator-approved Atlas trust-strengthening pass, 2026-08-21.

## D-23 ? 2026-08-21 ? Offline replay proposes before it teaches

Ruling: offline replay may rank episodes and propose a fact, skill, watch, or
correction, but it cannot verify, activate, or rewrite anything. Every proposal
is source-linked, stable across retries, pending review, and explicitly
non-mutating; failed or malformed evaluation remains unknown.
Why: reflection can discover useful patterns only if the system does not treat
its own synthesis as evidence or authority.
Source: operator-approved governed-replay build, 2026-08-21.

## D-24 ? 2026-08-21 ? Rehearsal tests proposals without promoting them

Ruling: a replay proposal may be counterfactually rehearsed against explicit
expected and forbidden outcomes. Every scenario must pass; a failed scenario
fails the rehearsal, and missing or malformed evaluation remains unknown. Even
a passing rehearsal stays pending review and cannot increase trust, grant
authority, activate work, or mutate memory.
Why: simulated success is useful evidence about a proposed change, but it is
not an independent observation of the real world or operator approval.
Source: operator-approved brain-function build order, 2026-08-21.

## D-25 ? 2026-08-21 ? Learning must manifest before mastery is proposed

Ruling: sourced knowledge is not mastery. A learning cycle must preserve an
application or teach-back, externally evaluated understanding, and successful
transfer in a distinct context before it may create a stable mastery proposal.
The proposal remains pending review, cannot activate a skill, and cannot mutate
memory; failed and unknown attempts remain in the append-only learning cipher.
Why: recall demonstrates availability, while mastery requires demonstrated use
and transfer without granting an agent authority to certify itself.
Source: operator-approved governed-learning build, 2026-08-21.


## D-26 · 2026-08-21 · Readiness separates evidence coverage from score

Ruling: an agent or repository dimension is scored only when it cites permitted evidence. Unknown dimensions remain unscored and reduce coverage; they never become zeroes. A weighted readiness result requires at least five of eight dimensions, while any public-ready state also requires owner opt-in, human review, and a specific publication approval record.
Why: collapsing missing evidence into failure creates false rankings, while publishing an automated score without ownership and review turns a useful delegation signal into an unsupported endorsement.
Source: operator-approved Breadcrumb Score build, 2026-08-21.

## D-27 · 2026-08-21 · A2A discovery may point to evidence without becoming a trust authority

Ruling: a public A2A Agent Card may carry a non-required Breadcrumb Score extension only when the assessment is published, human reviewed, publication approved, unexpired, target-matched, and digest verified. The exporter refuses local endpoints, unknown public fields, and mutation of a signed card; the provider must re-sign any changed signed card.
Why: discovery metadata can make delegation evidence easier to find without replacing A2A, turning a score into authentication, or exposing authenticated card data.
Source: operator-approved agent-to-agent revenue and outreach program, 2026-08-21.

## D-28 · 2026-08-24 · Scope is derived from trusted identity

Ruling: memory context exposed to an untrusted caller must resolve the current principal through a host-owned adapter and derive clearance from fixed policy. Request input never supplies principal, audience, role, or clearance; ungranted principals fail closed. The engine's direct audience argument remains a low-level composition primitive, not an authorization boundary.
Why: filtering works only when the caller cannot select a broader filter than its authenticated identity permits.
Source: operator-approved independent catalog gap closure, 2026-08-24.

## D-29 · 2026-08-26 · Research changes evidence before architecture

Ruling: Collaborative-intelligence sources use one versioned review method with common
fields, architecture-impact labels, corroboration states, explicit negative evidence,
and a ranked question queue. Metadata changes are backfilled across prior reviews;
analytical changes require rereading the source. A literature gap never proves this
repository fills it, and a new implementation never creates a principle by itself.
Why: separating method evolution from architecture evolution prevents a growing paper
catalog from becoming a machine for confirming the design it was meant to test.
Source: operator-approved ChatGPT research checkpoint, 2026-08-26.

## D-30 · 2026-08-26 · Breadcrumbs is the public cooperative-intelligence pattern layer

Ruling: Breadcrumbs extends beyond agent memory into a public, reusable pattern kit for
human-AI cooperation. It owns generalized research, methods, and patterns, while each
implementation retains its own source records, authority, and private operational context.
Research reaches the kit only through source-linked, bounded claims and does not trigger
an automatic runtime change.
Why: a public kit can make proven mechanisms reusable without becoming a second memory
store or disclosing the private systems that generated the lessons.
Source: operator direction, 2026-08-26.

## D-31 · 2026-08-27 · Cooperative intelligence is evaluated by separate concerns

Ruling: Breadcrumbs evaluates bounded shared work through orientation, handoff,
correction, ownership, and recovery, while keeping individual throughput, quality, cost,
and burden as separate outcomes. A result must name its comparison baseline and may not
collapse those concerns into one collaboration score.
Why: a system can improve an individual's work without improving coordination, or hide a
correction and authority failure behind a faster result.
Source: operator-approved Breadcrumbs research expansion, 2026-08-27.

## D-32 · 2026-08-27 · Research synthesis is claim-centered and profile-based

Ruling: Method v2.0 treats a bounded claim, not a paper, as the unit of synthesis.
Sources retain identity and review history, receive a visible structural appraisal,
and link to stable claim IDs. Confidence remains a profile of directness, validity,
independence, consistency, transfer, and durability rather than one score. Source
count never substitutes for evidence independence, and research promotion requires
a null case, expiry conditions, and owning-system evidence.
Why: the 100-source audit showed that unique papers can share authors, datasets,
benchmarks, judges, or narrow settings; source identity verification does not verify
a claim; and a single confidence label hides the exact evidence weakness that should
drive the next test.
Source: operator-approved Method v2.0 and 100-source re-evaluation, 2026-08-27.

## D-33 · 2026-08-27 · Repository landscapes appraise mechanisms, not products

Ruling: public repository comparisons bind every observation to a canonical
repository, exact commit, evidence depth, and claim link. They classify visible,
partial, not-observed, and out-of-scope mechanisms without calculating a composite
framework score or inferring runtime performance from repository features. Maintenance,
migration, archive, licensing, and hosted-product boundaries remain explicit.
Why: feature counts and README claims can show how a theory was codified, but they do
not establish collaboration benefit, authority quality, recovery performance, cost, or
independent verification. Versioned observations make the map reproducible and allow
later code tracing without silently rewriting the earlier screen.
Source: operator-approved collaborative-intelligence repository landscape, 2026-08-27.

## D-34 · 2026-08-27 · Popularity selects candidates within an aspect

Ruling: repository star counts may order discovery inside a named
collaborative-intelligence aspect, but they never score quality or decide promotion.
The landscape deduplicates product lineages and overlapping mechanisms, retains a
lower-starred repository when it uniquely fills a mechanism gap, and records popular
screened-out alternatives with reasons and an observation date.
Why: a raw popularity ranking would overrepresent broad, older platforms and hide
specialized work on authority, memory, evaluation, observability, and guardrails.
Source: operator-approved 25-repository popularity-directed expansion, 2026-08-27.

## D-35 · 2026-08-27 · The repository landscape stops at mechanism-family saturation

Ruling: the public repository landscape may expand to 100 pinned,
README-screened repositories to cover orchestration, multi-agent research,
memory, retrieval, evaluation, guardrails, gateways, sandboxes, protocols, and
coding-agent control planes. Research artifacts and maintenance lineages remain
explicit lifecycle states. After this breadth pass, new repositories enter only
when they close a named mechanism gap; the default next step is code tracing and
bounded execution, not a higher source count.
Why: the 75-repository expansion closes major category gaps but confirms that
additional overlapping frameworks would add maintenance burden faster than
claim confidence. Depth is now the limiting evidence factor.
Source: operator-approved 100-repository landscape expansion, 2026-08-27.

## D-36 · 2026-08-28 · Breadcrumbs has a public web front door

Ruling: Breadcrumbs presents its public research, repository landscape, memory patterns,
workflow patterns, and evaluation method through a GitHub Pages site called Breadcrumbs.
The primary visualization is the Trail Map. Research and repository catalogs are separate,
searchable pages with item detail pages and typed related links. Multi-dimensional profiles
keep popularity, evidence, directness, durability, and mechanism coverage separate rather
than collapsing them into one score. GitHub remains authoritative, and the site is built
only from public repository records.
Why: the repository contains linked evidence, but a file tree is not an accessible discovery
interface for people who do not already know how to navigate repositories.
Source: operator direction, 2026-08-28.

## D-37 · 2026-08-28 · Breadcrumbs extends the established editorial brand

Ruling: the Breadcrumbs web surface uses the established forest-green, jade, antique-gold,
and ivory visual system with Georgia display type and Arial working type. It does not use
the navy technical-dashboard palette inferred from the older repository banner.
Why: Breadcrumbs belongs to the same public body of work as the 825 and Architect's
Sandbox materials, so its visual identity should make that relationship recognizable.
Source: operator correction against the first public-site release, 2026-08-28.

## D-38 · 2026-08-28 · Catalog ratings remain multi-dimensional profiles

Ruling: the research catalog displays evidence order, directness, horizon, linked claims,
and citation signal as separate fields. Evidence order uses directness, then horizon, then
stable source ID. Citation popularity remains not collected until a reproducible source is
approved. The repository catalog displays global star rank, within-aspect star rank,
mechanism coverage, linked claims, evidence depth, and lifecycle separately.
Why: combining unlike signals into one rating would imply a quality verdict the evidence
does not support. Separate dimensions remain sortable, interpretable, and correctable.
Source: operator direction for expanded catalog ratings, 2026-08-28.

## D-39 · 2026-08-28 · Public profiles explain relationships visually

Ruling: the public Jarvis profile includes a content-free operating map from repository
truth through governed routing, bounded execution, and independent verification.
Repository and research profiles use small visual signal charts alongside prose. Charts
describe observed dimensions only and never imply a composite quality score.
Why: the public site needs to make system relationships and review findings legible without
copying the private Operator Board or adding unsupported decorative claims.
Source: operator direction for richer public profiles and visual explanation, 2026-08-28.

## D-40 · 2026-08-28 · Public labels must explain the model without prior knowledge

Ruling: public profiles use full claim titles, expanded evidence-family names, broader
repository categories, and specific selection lenses. Category rank replaces rankings
inside mostly unique selection lenses. Related items rank by shared claims and stop at five.
Why: internal IDs and one-of-one ranks are traceable but not meaningful to a new reader.
Source: operator walkthrough of the first public profile release, 2026-08-28.

## D-41 · 2026-08-28 · Claims use one interactive landscape, not a long list

Ruling: the public claim register presents four thematic clusters around Breadcrumbs.
Selecting a claim updates one detail inspector. Wide screens show four clusters, the
in-app view shows two, and only narrow mobile screens collapse to one column.
Why: the relationship among claims is more important than their document order.
Source: operator walkthrough of the graph-only claim release, 2026-08-28.

## D-42 · 2026-08-28 · Hugging Face is an evaluation lab, not a memory store

Ruling: Breadcrumbs may use public synthetic cases and Hugging Face model inference to
compare orientation accuracy, token use, and latency across model tiers. The benchmark
must keep measures separate, retain repository ownership, exclude private records, and
require execution-time confirmation before any potentially billable inference call.
Why: the first useful Hugging Face integration is evidence for the Version 1.5
orientation objective, not another memory backend or an uncontrolled data boundary.
Source: operator direction, 2026-08-28.

## D-43 · 2026-08-28 · Live benchmark matrices require a one-call preflight

Ruling: a Hugging Face benchmark must validate one live response for transport parsing,
authentication, and account capacity before launching a multi-call matrix. The runner
fails closed after a preflight error and retains only response metadata and a digest when
the provider payload cannot be parsed.
Why: the first live orientation run recorded sixteen unusable attempts. Evidence:
`responses.jsonl` and `results.json` from the local 2026-08-28 run. The light-model
responses could not be parsed, the strong-model responses reached payment-required, and
no valid comparative scores were produced. The correction is transport-aware parsing
plus a mandatory one-call preflight. Follow-up diagnostics showed that Granite 4.2's
default thinking mode exhausted the original 160-token generation cap and returned empty
final content, so the benchmark now disables thinking explicitly and uses the model-card
sampling defaults. The prevention check is a passing preflight artifact with non-empty
final content before any matrix authorization.
Source: live benchmark correction, 2026-08-28.

## D-44 · 2026-08-29 · Breadcrumbs owns the portable public repository ledger

Ruling: Breadcrumbs is the authoritative owner of the reusable, public repository
assessment ledger. Imports use case-insensitive owner/repository keys, preserve
evidence-only aliases and unknown fields, collapse duplicates, and never grant
authority. Operated repositories, private portfolio identities, internal paths, and
private evidence remain outside the public artifact and are reported only as aggregate
exclusions.
Why: a reusable public assessment layer belongs with the public pattern kit, while
restricted systems retain only their own evidence and data.
Source: operator repository-ownership correction, 2026-08-29.
