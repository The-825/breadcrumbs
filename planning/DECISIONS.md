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
