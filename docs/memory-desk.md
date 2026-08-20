# The memory desk: retrieval for the cheapest session you will ever run

> Pairs with [catalog-routing.md](catalog-routing.md), whose flat-index
> objection this essay answers, and with [floating-memory.md](floating-memory.md),
> which owns the write side of a fleet. The runnable kit is
> [templates/memory-desk/](../templates/memory-desk/). Assumes you run coding
> agents against a repo that has accumulated settled facts: thresholds, paths,
> conventions, gotchas, rulings.

## Design for the weakest reader on their worst day

Every memory system in this kit was written by strong models on high effort,
and most of it will be read by weak ones on low. That asymmetry is the design
problem, and most memory architectures ignore it. They assume the reader can
classify a question into a destination, choose between four ledgers, parse a
YAML catalog, and remember a protocol it read forty turns ago. A frontier
model on a good day does all of that. The session you actually route your
volume to, the cheap tier on minimal effort, fails each step some fraction of
the time, and the failures compound into the familiar shapes: the confident
answer from a stale recollection, the first plausible grep hit taken as
truth, the rules file re-read whole for one threshold.

Watch what the weak session actually gets wrong and a pattern shows: it fails
at judgment, not at execution. It runs commands fine. It reads ten lines fine.
What it fumbles is deciding which of five places to look, or noticing that a
question even has a settled answer. So the refinement is one move:

**Take every judgment out of retrieval and move it into maintenance.**

Retrieval becomes mechanical: one verb, exact match first, tiny payloads,
misses that print the next command. Maintenance becomes intelligent: a strong
model, on a schedule, curates what the mechanical layer serves. The cheap
session executes; the expensive session, visiting weekly, does the thinking.
An airport does this deliberately: the information desk exists so the
first-time traveler never needs terminal knowledge, because the person behind
the desk has it for them.

## The desk

Five parts, each with one job:

- **The kernel** (`MEMORY.md`, capped at 60 lines, enforced): the only memory
  file a session reads whole. It holds the frozen floor facts, the one lookup
  move, and the capture habit. Nothing else, because every kernel line taxes
  every session ([context-budget.md](context-budget.md)).
- **The index** (`index.tsv`): one row per settled fact: key, aliases, answer,
  source, checked date. Flat on purpose, tab-separated on purpose. It is a
  database that happens to be greppable text, not a document anyone reads.
- **The door** (`mem`): a stdlib-only CLI. `mem <words>` answers by exact key
  or alias, then by ranked token overlap, capped at three rows. `mem add`
  appends raw capture to the journal. `mem reject` retires a wrong answer into
  a tombstone that `check` then enforces against, and `mem recheck` reports rows
  whose source moved after they were last checked. `mem check` is the integrity gate:
  duplicate keys, dead sources, oversized kernel, malformed rows, all CI-able.
- **The journal** (`journal.jsonl`): append-only capture. Any session records
  a durable fact in one command, unpolished, and moves on.
- **The gardener**: a scheduled pass with a written contract: promote journal
  entries into rows, dedupe, re-verify stale rows at their sources, retire
  with stated reasons, trim the kernel. Its changes arrive as a PR behind the
  approval label.

Plus a push layer of three hooks, because pull-based memory relies on the one
thing the weak session lacks, remembering to look. The kernel is injected at
session start. The prompt is run through the index at submit time, so a
question whose answer is settled gets the row injected before the model
thinks to search. And a file-scoped note (an alias like `file:src/sync.py`)
is injected when that file is first edited, which is the moment the gotcha
about it matters.

## Why a flat index after all

[catalog-routing.md](catalog-routing.md) argues against flat indexes: past
one screen, the index becomes the thing nobody keeps current. That objection
is correct for an index that people read and maintain by hand, and it is the
reason the desk changes three terms of the tradeoff at once:

1. **Queried, not read.** No session ever loads the index; it asks the door.
   Size stops mattering to the context window, so the index can afford to be
   complete.
2. **Gardened, not remembered.** Currency is a scheduled job with a contract,
   not a courtesy. The failure mode "nobody adds the line" becomes "the
   gardener's next pass promotes the journal entry," and the journal entry
   took one command at the moment the fact appeared.
3. **Gated, not trusted.** `mem check` fails the build on rot: a source path
   that no longer resolves, a key collision, a kernel past its cap. An index
   that can fail CI cannot silently lie for weeks.

The catalog's three hops also carry a cost that only shows at the cheap tier:
hop one is a classification, and classification is judgment. Catalog routing
stays the right shape for essay-shaped corpora, where the answer is a
document rather than a line. The desk fronts it: fact-shaped questions end at
a row, and a row whose answer is genuinely a document points at it, so the
hop count for the weak session is one, or two when the answer is long-form.

## Rules for the mechanical layer

Each of these exists because its absence is a failure you can watch a cheap
session have:

1. **One verb.** A session that must choose between stores chooses wrong.
   Every factual lookup is `mem <words>`; which store answers is the desk's
   implementation detail.
2. **Exact before clever.** Ranked matching is a fallback, not the interface.
   Keys and aliases are phrased the way sessions ask, and the best source of
   phrasing is a real miss: the query that failed becomes the new row's key.
3. **A miss is an instruction.** The tool never returns a bare "not found,"
   because a dead end invites the model to guess. The miss prints a scoped
   grep, then a narrow read, then the `mem add` that writes the answer back.
   The weak session's next action is never a judgment call.
4. **Payloads stay tiny.** A hit is three lines: answer, source, checked date.
   Three hits maximum. Retrieval that dumps a screen re-creates the problem
   the desk exists to solve.
5. **Push beats pull.** The hooks deliver the kernel, the matching rows, and
   the file notes at the moments they matter. A protocol the model must
   remember is a protocol the cheap tier does not have.
6. **Degrade to grep.** The index is plain text with tabs. When the tool is
   unavailable, `grep -i '<word>' memory/index.tsv` reads the same rows. The
   format is the interface; the CLI is convenience.
7. **Freshness is visible at read time.** Every row prints its checked date,
   and a row past the stale horizon prints a flag. The reader learns to trust
   dated answers and to re-verify flagged ones, which is the correct posture
   toward any memory.

## The write path: journal now, garden later

Same-turn capture is the right rule and the usual one, and it fails in
practice for a specific reason: capturing well is expensive. Choosing the
right ledger, phrasing the entry, finding the source, all mid-task, is
exactly the judgment load that gets dropped under pressure. So the desk
splits the act. Capture is one command with no quality bar beyond "one
sentence, typed": cheap enough that it actually happens in the turn. Quality
control moves to the gardener pass, where a strong model with time promotes,
rephrases, deduplicates, and sources the entry properly, and where a reviewer
sees the result as a PR. The fact survives the turn it landed in; the
polishing happens where polishing is safe.

## What the desk is not

It is the read side, deliberately narrow. Conduct rules stay in the rules
file; an index row states facts, not obligations. Multi-session write
concurrency, completion claims, and trust decay belong to the fold protocol
in [floating-memory.md](floating-memory.md); the desk assumes facts arrive
through the journal of a single repo. Long-form reasoning lives in docs, and
rows point to it rather than compress it. And the desk does not verify its
own answers beyond dates and dead links; a row is as good as its last
gardening, which is why the date ships with every hit.

## Adopting it

An afternoon, in this order: copy the kit, write the kernel (floor first),
seed the index by splitting your rules file into answers (rows) and conduct
(rules), wire the three hooks, add `mem check` and the self-tests to CI, and
schedule the gardener. The full steps are in the kit's
[README](../templates/memory-desk/README.md). Then measure it the way
[memory-measurement.md](memory-measurement.md) prescribes: every row is an
address a probe can ask for, so reachability stops being a hope.

Start even smaller if you want the one-sign version: a twenty-row index and
the prompt-time hook, nothing else. That alone converts the most common
weak-session failure, the confident stale answer, into an injected row with a
source and a date.
