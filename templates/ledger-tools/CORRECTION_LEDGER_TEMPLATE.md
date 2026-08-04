# Correction ledger template

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

The [self-improvement loop](../../docs/self-improvement-loop.md) feeds on corrections:
things that were wrong and got caught. This ledger is where they land, with one
admission rule that keeps the loop honest.

## The oracle taxonomy (the admission rule)

A correction enters the ledger ONLY when it is anchored to an objective oracle:

| oracle | what it is |
|---|---|
| `ci_failure` | a red CI check: a lint guard, a parse check, a failing unit or route test |
| `data_assertion` | a tripped data-integrity assertion in the pipeline |
| `operator_ruling` | the operator corrected it: the human ground truth |
| `reverted_pr` | a merged PR was reverted or rolled back |

Model-vs-model disagreement is never a correction. A stronger model "disagreeing" with
a cheaper one has no ground truth behind it, and neither does a model's own audit pass;
admitting either would train the loop on opinion, and a self-improvement loop that
learns from the wrong signal is worse than none, because it optimizes a proxy. If you
wrap appends in a script, enforce the oracle set there fail-closed: an unrecognized
oracle is rejected, not stored.

## Line format

Append-only JSONL, one correction per line, lines never edited or deleted:

```json
{"date": "<YYYY-MM-DD>", "zone": "<area of the codebase or work>", "oracle": "<one of the four>", "tier": "<model tier that produced the corrected work, or unknown>", "ref": "<the oracle's evidence pointer: PR number, check name, ruling and date>", "note": "<one line: what was wrong and the durable lesson>"}
```

`ref` is load-bearing: every correction must be verifiable by following it back to the
red check, the tripped assertion, the ruling, or the revert. Example lines, invented
values:

```json
{"date": "2026-01-12", "zone": "reports", "oracle": "operator_ruling", "tier": "unknown", "ref": "rules-file thresholds section; operator ruling 2026-01-12", "note": "the discount floor is 0.745 not the spoken 0.75; a confident paraphrase dropped the rounding nuance"}
{"date": "2026-02-03", "zone": "frontend", "oracle": "ci_failure", "tier": "fast", "ref": "guard_no_inline_style_script, PR 41", "note": "inline style block added during a small fix; moved to the stylesheet, small fixes get the same floor"}
{"date": "2026-02-19", "zone": "migrations", "oracle": "reverted_pr", "tier": "mid", "ref": "PR 57 reverted by PR 58", "note": "a migration renamed a column in place instead of adding a new one; forward-only means add and deprecate"}
```

## Hygiene

The same rules as the conclusions store: no PII or sensitive data in any line
(reference work by feature slug and PR number, never by a person's identifier), the
[union-merge](union-merge.md) setting once the ledger has parallel writers, and the
[provenance fields](PROVENANCE.md) if you want per-line origin tracking. What the
ledger feeds (audit rates, escalation, the retro) is downstream machinery; the ledger
itself stays a flat, verifiable record of what reality corrected.
