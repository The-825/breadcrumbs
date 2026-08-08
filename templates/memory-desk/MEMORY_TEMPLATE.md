# MEMORY.md · <repo name> memory desk kernel

<!-- Copied from templates/memory-desk/MEMORY_TEMPLATE.md. Fill the angle
     brackets, delete this comment, rename to MEMORY.md. mem check fails when
     this file grows past 60 lines; the cap is the design, not a suggestion. -->

Read this file whole. It is the only memory file you read top to bottom;
everything else is queried.

## The one move

Every factual question about this repo starts with:

    memory/mem <words>

`memory/mem deploy gate` · `memory/mem where do rulings go` · `memory/mem <filename>`

A hit gives the answer plus its source and a checked date. A miss prints
your next command; run it. Never answer from recall what the index can
answer: recall drifts, rows carry sources.

No shell? The index is plain text: `grep -i '<word>' memory/index.tsv`

## Floor: the facts that must never be wrong

Frozen verbatim, pinned by tests, never edited by the gardener. Keep this
list at ten lines or fewer; a floor nobody can hold in view is not a floor.

1. <the fact whose miss produces an unsafe write>
2. <the invariant that broke production once>
3. <the safety rule that survives every session>

## Capture

A durable fact, ruling, or gotcha lands the same turn it appears:

    memory/mem add "<one sentence>" --type decision --source <path or PR>

Journal now, polish never. The gardener curates weekly; your only job is
to not let the fact die in the transcript.

## The desk, one line each

- `index.tsv`: every settled fact as key, aliases, answer, source, checked date
- `journal.jsonl`: raw capture, append-only, promoted weekly
- `gardener/`: the curation contract; its changes arrive as a reviewed PR
- `hooks/`: the desk comes to you at session start, prompt time, and first edit
