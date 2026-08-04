# breadcrumbs

*One person's working answer to a specific problem: how do I get the most out of AI
coding models without re-explaining everything at the start of every session? Not a
product, not a framework launch. A pattern I built for my own work that I think you can
steal, with any model, in an afternoon. I'm sharing it because the parts that worked
surprised me and the part that failed surprised me more.*

## The clothes pile

There is a spot in every house where the clothes pile forms. You can demand better
memory of yourself, or you can notice where the pile forms and put a basket there. Then
a light above the basket. Then move the basket closer to the laundry. You never trained
your memory. You placed cues where the behavior already happens, and the environment
started doing the remembering.

That is the whole idea. AI agents forget everything between sessions, and the industry's
answer has mostly been bigger recall: vector stores, knowledge graphs, retrieval layers.
Those answer "what should the agent remember?" My problem was different. I run many
agent sessions a week against one production system, and what kept breaking was not
recall. It was that one session would claim something was done when it wasn't, or redo
work a yesterday-session already did, or act on a fact that had changed underneath it.
And every fresh session opened with me re-framing, re-contextualizing, re-explaining,
paying the same tax again before any real work happened.

I did not need a smarter archive. I needed baskets: breadcrumbs left where the next
session already walks.

## The cues, at the moments they fire

My setup is ordinary on purpose: a git repo, some shell hooks, plain text and JSONL
files. No memory vendor, no new database. The cues live at the moments where agent
behavior already happens:

- **At the door (session start).** Every session boots with a small injected packet:
  the handful of facts that must never be wrong (frozen and test-pinned, so a missing
  line fails a build), the open obligations nobody has finished, and what changed since
  this session last acted. The agent does not go looking. The environment says it at
  the door.
- **At the claim (finishing work).** A session cannot just say "done." It records what
  it finished, and the record is refused if obligations still dangle: an unshipped
  follow-up, a "part 2 of 3" left hanging. It can park work with the leftovers named,
  or formally defer an item with a deadline, the way aircraft defer an inoperative part
  under a minimum equipment list. What it cannot do is quietly drop the leftover.
- **At the boast (claiming certainty).** An agent never marks its own claim "verified."
  Verified requires naming an objective check: a CI result, a data assertion, a human
  ruling. Everything else is stamped "asserted," and every future reader sees
  "re-verify before acting." Most memory systems let models grade their own homework.
  Mine are not allowed to.
- **At the handoff.** When one session hands work to the next, the handoff is a written
  brief plus a replay guard: read what your predecessor actually did before you redo
  it. Decisions get written down the same turn they land, because a ruling that lives
  only in a transcript gets re-litigated by the next session, every time.
- **Underneath everything.** Nothing is edited in place. A wrong entry is superseded by
  a newer one that names what it kills. The record of being wrong survives.

Total cost: a few scripts, git, and discipline encoded as refusals rather than
reminders.

## The day it caught itself

Here is the part that made me want to publish, told plainly because it is more
convincing than any benchmark.

My memory files have a size cap, and a guard that truncates runaway injections. One day
I raised the cap and recorded, in the permanent decision ledger, that the guard was
raised in lockstep. Weeks later I ran an audit pass over the whole memory corpus,
agent-driven, checking every documented claim against the actual code. The audit found
the guard was never raised, and the ledger entry even named the wrong file. Worse:
because the guard was still at the old size, every session's boot memory had been
silently truncated mid-file for days, and the audit could point at that morning's own
boot as the live evidence.

The fix took an hour: the guard resized off measured data, a test that now fails if
anyone shrinks it without re-measuring, and the false ledger entry superseded on the
record by a correction that explains exactly what was wrong. Nothing was deleted. The
system carries an honest scar: proof that a claim was made, believed, caught, and
corrected.

A memory system that can believe a false memory about itself, notice, and correct the
record is worth more to me than one that promises never to be wrong.

## Steal this: start in one afternoon

Everything in this repo is a starting piece for the pattern above, extracted from the
system I actually run, with the domain scrubbed out. Nothing depends on which model you
use; a fleet member is anything that can read a file at start and append a line at the
end. Do these in order and stop when you have had enough for the day:

1. **A handoff file.** Copy [`templates/SESSION_STATE_TEMPLATE.md`](templates/SESSION_STATE_TEMPLATE.md)
   to your repo root. Only what is in flight: branch, open PR, half-done edits, next
   steps. Refresh it on a trigger word you say out loud, not on "keep it updated,"
   which means never.
2. **A decisions ledger.** Copy [`templates/DECISIONS_TEMPLATE.md`](templates/DECISIONS_TEMPLATE.md).
   Numbered entries, newest last, written the same turn the call lands.
3. **A settled-facts store.** Copy [`templates/CONCLUSIONS_TEMPLATE.md`](templates/CONCLUSIONS_TEMPLATE.md).
   One fact per line, read at session start, so nothing already known gets re-derived.
4. **A rules file.** Copy [`templates/CLAUDE_TEMPLATE.md`](templates/CLAUDE_TEMPLATE.md)
   and delete what does not apply. This is the file every session boots from, the
   highest-leverage basket in the house.
5. **A merge gate with teeth.** [`ci-kit/workflows/`](ci-kit/workflows/) ships a
   fail-closed automerge: merges happen only when every required check is green on the
   exact head commit, and only after a human applies an approval label. Read
   [`AUTOMERGE_GOTCHAS.md`](ci-kit/workflows/AUTOMERGE_GOTCHAS.md) first; the naive
   version has about ten non-obvious ways to fail.

## What is in here

| Directory | What it gives you |
|---|---|
| [`templates/`](templates/) | Copy-and-adapt working files: rules file, session handoff, decision and authority ledgers, incident and ADR templates, slash commands, hooks, a test-harness skeleton |
| [`ci-kit/`](ci-kit/) | The runnable part: lint guards that ship with fixtures proving they bite, a migration runner with policy checks, and the fail-closed merge gate |
| [`skills/`](skills/) | Paste-able rule sets for your own rules file |
| [`checklists/`](checklists/) | Two-minute operational checklists |
| [`docs/`](docs/) | The reasoning behind each piece, including [`floating-memory.md`](docs/floating-memory.md), the fuller memory architecture the cues above grew into |
| [`playbook/`](playbook/) | How the pieces fit together, and patterns for running more than one agent at a time |

## What I have not proven

Honesty section. This runs in one office, mine, at one scale, a few hundred agent
sessions a month. My evidence is incidents caught and work not redone, counted by hand;
the instrumentation that will give me real usage numbers is new, and I would rather say
"counted by hand" than dress it up. Structured handoffs help the site that designed
them more than anyone else; that finding comes from hospital shift-change research and
I assume it applies to me too. If you try this pattern and it fails somewhere, that is
exactly the report I want.

## Try it

Start with one basket, not the whole house: pick the single moment your agents most
often act on stale state, and place one cue there that fires automatically. For me that
was session start. Add the refusal second; it is the piece with teeth. Then open an
issue here and tell me what happened, what worked, what broke, what you changed. I am
one investigator with one data point, and the pattern gets better the more houses it
runs in.

Everything is MIT licensed. See [LICENSE](LICENSE). Take it, adapt it, ship it.

*I'm also writing the longer story of the system this came from, From Archivist to
Architect. More on that another day; the repo stands on its own.*
