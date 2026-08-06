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
