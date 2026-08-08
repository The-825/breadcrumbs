# The memory desk

> Assumes: a git repo, a POSIX shell, python3 (3.8+, stdlib only). The hooks
> target Claude Code's settings.json contract and port to any harness with
> session-start, prompt-submit, and post-tool events. The gardener workflow
> template assumes GitHub Actions; the gardener contract itself is
> host-neutral. The reasoning behind the design is
> [docs/memory-desk.md](../../docs/memory-desk.md).

The failure this kit closes, the way it actually happens: you hand a repo to a
cheap model on low effort and ask a question the repo has answered before. It
does one of three things. It re-reads the whole rules file and burns the
window. It greps the tree and takes the first plausible hit, which is the
dangerous one. Or it answers from recall of some earlier session, which is the
same as guessing. All three are one failure: retrieval that depends on the
model being good at retrieval.

The desk inverts that. **Retrieval is mechanical; maintenance is intelligent.**
Any session, any tier, has exactly one move (`memory/mem <words>`), exact
match answers first, and a miss prints the next command to run. The judgment
lives where a strong model visits on a schedule: the gardener pass that
promotes, dedupes, and re-verifies the index. The cheapest session executes;
the curation carries the discipline.

Like the information desk in a terminal: the first-time traveler does not
learn the building, they ask the desk, and the desk is staffed by someone who
does know the building.

## The pieces

| File | What it is |
|---|---|
| [`mem`](mem) | The one door: lookup, capture, and integrity check in one stdlib-only CLI. Exit codes are the interface: 0 hit, 1 miss, 2 defect. |
| [`index.tsv`](index.tsv) | The fact index: key, aliases, answer, source, checked date, one row per settled fact. Ships seeded with rows that describe the desk itself. |
| [`MEMORY_TEMPLATE.md`](MEMORY_TEMPLATE.md) | The kernel: the one file a session reads whole. The one move, the frozen floor, the capture habit. `mem check` fails it past 60 lines. |
| `journal.jsonl` | Raw capture, append-only, created by the first `mem add`. Nothing edits it; the gardener promotes from it. |
| [`hooks/`](hooks/) | The push layer: kernel at session start, index hits at prompt time, file-scoped notes at first edit. Registration snippet included. |
| [`gardener/`](gardener/) | The curation contract and a scheduled trigger, so index quality is a job with a cadence, not goodwill. |
| [`tests/`](tests/) | Subprocess self-tests for the CLI, ending with the shipped kit passing its own `mem check`. |

## How a lookup flows

```
memory/mem where do rulings go
  exact key or alias match ......... print the row, done        (exit 0)
  else ranked token overlap ........ print up to 3 rows, done   (exit 0)
  else miss ........................ print the ladder           (exit 1)
      1. grep -ril '<word>' . | head -5
      2. read the narrow range the grep finds
      3. memory/mem add "<the answer>" --key '<what you asked>' --source <path>
```

The ladder is the point. A miss is never a dead end that invites guessing; it
is an instruction whose last step writes the answer back, so the next session
that asks the same thing gets a hit. The query that missed becomes the new
row's key, which is why keys stay phrased the way sessions actually ask.

## Install

1. Copy this directory to `memory/` at your repo root, and
   `chmod +x memory/mem`.
2. Rename `MEMORY_TEMPLATE.md` to `MEMORY.md`, fill the placeholders, and put
   your floor facts in (ten lines or fewer; freeze them, pin them with a test).
3. Seed the index from your rules file: every line that ANSWERS a question
   (a threshold, a path, a convention, a gotcha) becomes a row. Lines that
   COMMAND behavior stay rules. This split is the whole adoption: rules file
   for conduct, index for facts.
4. Keep the shipped self-describing rows; they answer the questions new
   sessions ask about the desk itself.
5. Wire the hooks: merge [`hooks/settings-snippet.json`](hooks/settings-snippet.json)
   into your harness settings, then trip each hook once on purpose. A hook you
   never watched fire is a silent hole.
6. Add two lines to CI: `memory/mem check` and
   `python3 memory/tests/test_mem.py`. The index cannot rot silently once the
   build fails when it does.
7. Copy [`gardener/gardener.yml`](gardener/gardener.yml) into
   `.github/workflows/` and read [`gardener/GARDENER.md`](gardener/GARDENER.md)
   once. Point your rules file at the desk with three lines: every factual
   lookup starts at `memory/mem`; capture with `memory/mem add`; read
   `memory/MEMORY.md` at boot.

## Pitfalls

- **Keys must not begin with `add` or `check`**; those are subcommands, and
  `mem check` refuses such keys so the collision cannot lurk.
- **One line per answer.** An answer that wants a paragraph is a doc; write
  the doc, point the row's source at it, and let the answer say what is there.
- **A fact has one home.** The row either is the home (a one-liner) or points
  to it, never both, or the two copies drift and the row wins arguments it
  should lose.
- **Do not hand-polish the journal.** It is raw by design; polish happens in
  the gardener pass, where it is reviewed.

## Degradation ladder

Each layer failing leaves a working desk underneath. No hooks: the kernel
still says the one move, because the rules file points at it. No python: the
index is tab-separated text, and `grep -i '<word>' memory/index.tsv` reads
the same rows. No gardener: `mem check` still fails CI on dead sources and
collisions, so the index can stall but not silently lie. The desk never has a
single point of failure between a session and a settled fact.

## Where it sits among the other pieces

The desk is the read side of a memory system, not the whole of one. Your
rules file keeps conduct; the [conclusions store](../CONCLUSIONS_TEMPLATE.md)
can keep its role as the append-only settled-facts ledger, with the index
fronting it row by row. Three-hop
[catalog routing](../../docs/catalog-routing.md) stays right for essay-shaped
corpora; the desk sits in front for fact-shaped questions. The write side of
a multi-session fleet (folds, verification, decay) is
[floating memory](../../docs/floating-memory.md), and the measurement layer
that proves any of it surfaces is
[memory measurement](../../docs/memory-measurement.md).
