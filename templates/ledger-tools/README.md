# Ledger tools

The capture habit gets a conclusions ledger written ([docs/decision-capture.md](../../docs/decision-capture.md), base line format in [CONCLUSIONS_TEMPLATE.md](../CONCLUSIONS_TEMPLATE.md)). This directory is about the harder half: keeping the ledger trustworthy after months of entries, several writing surfaces, and a codebase that keeps moving underneath it.

| File | What it is |
|---|---|
| [PROVENANCE.md](PROVENANCE.md) | Three optional provenance fields (`src`, `verified`, `by`) extending the base entry format |
| [conclusions_audit.py](conclusions_audit.py) | Staleness auditor: classifies every entry STALE / AGING / SPECIAL / OK and checks `obsoleted_by` chains |
| [sample_conclusions.jsonl](sample_conclusions.jsonl) | Synthetic six-line fixture that demonstrates every verdict |
| [capture_nudge.py](capture_nudge.py) + [capture-nudge.md](capture-nudge.md) | UserPromptSubmit hook that injects a same-turn capture reminder when a prompt contains ruling-shaped language |
| [union-merge.md](union-merge.md) | The `merge=union` gitattributes setting for parallel appenders, with the cases where it is unsafe |
| [retrieval_exam.py](retrieval_exam.py) | Retrieval exam: per-entry reachability verdicts against your real tree, an injection-lane probe, a use-stamp readout, and a ratchetable baseline. Asks whether entries can be SEEN, where the auditor asks whether they are still TRUE |
| [sample_probes.json](sample_probes.json) | Four session-start conditions for the exam's lane probe, written against the sample ledger |
| [memory_engine.py](memory_engine.py) | Three-tier runnable memory (working state, append-only episodes, semantic facts with asserted-vs-verified status): compaction flushes down instead of deleting, facts can cite their exact source episodes, contradiction checks produce typed review-only proposals and keep evaluator failures unknown, verification requires a distinct tool or human authority so agent repetition cannot self-promote, rejected values leave tombstones that block silent re-assertion, and deterministic retrieval fuses lexical, action/tag, and recency ranks while preserving as-of replay, valid-at windows, and audience scoping |
| [memory_engine_exam.py](memory_engine_exam.py) + [memory_engine_golden.json](memory_engine_golden.json) | Golden-query regression exam over the runnable memory engine: expected and forbidden hits for deterministic fusion, public-scope exclusion, learned-time replay, valid-time windows, and verification-time masking |
| [budget_loans.py](budget_loans.py) | Context-budget raises as loans: a due open loan is a red check, and a cap raise without an open loan record fails the gate, so the always-loaded surface cannot ratchet up with no single accountable decision |
| [SEARCH_MISSES.md](SEARCH_MISSES.md) | Append-only ledger of lookups that found nothing, each carrying the repo path where the answer should live, so a gap becomes a scoped task instead of evaporating with the session |
| [CORRECTION_LEDGER_TEMPLATE.md](CORRECTION_LEDGER_TEMPLATE.md) | Append-only corrections ledger admitting only entries anchored to an objective oracle (red CI check, tripped data assertion, operator ruling, reverted PR), so the self-improvement loop cannot optimize a proxy |

One known gap: the auditor predates the dated `obsoleted_by` grammar (`path@date` / `path@date#n`, CONCLUSIONS_TEMPLATE.md v3.1) and reports those pointers as unresolved; a curation pass or a future auditor update handles them.

The four pieces cover a ledger entry's whole life: it gets written at all (the nudge), it carries its origin and last-checked date (provenance), its decay gets measured instead of discovered (the auditor), and parallel writers stop fighting over the end of the file (union merge).

The search-miss ledger covers the case none of those reach: the entry that was never written, discovered by somebody going to look for it. Its readout, and the three other instruments that tell you whether your memory layer surfaces at all, are in [docs/memory-measurement.md](../../docs/memory-measurement.md).

## Try it

From the repo root:

```
python3 templates/ledger-tools/conclusions_audit.py templates/ledger-tools/sample_conclusions.jsonl --root .
python3 templates/ledger-tools/conclusions_audit.py --selftest
```

And the retrieval exam over the same fixture:

```
python3 templates/ledger-tools/retrieval_exam.py templates/ledger-tools/sample_conclusions.jsonl \
    --root . --probes templates/ledger-tools/sample_probes.json
python3 templates/ledger-tools/retrieval_exam.py --selftest
```

On the sample that reports one unreachable entry (the retired path, which the auditor
separately calls STALE, the same entry failing both ways), a lane that varies across all
four probes, one entry injected on every probe with no use stamp, and one FORBIDDEN HIT:
the superseded entry (line 6, `obsoleted_by` a note that no longer exists) still wins
retrieval on the probe touching its file, so the model would see the old ruling.
Correction that stops at the ledger row and never reaches the lane is not correction;
`--fail-on-forbidden` turns that finding into a red exit for CI. Drop the `--probes`
flag and the exam derives probes from the tree instead, which is a smoke test rather than
an answer: the derived probes never touch the ledger's keyed files, so it reports
`UNEXERCISED` instead of pretending to a verdict.

The first auditor command audits the sample fixture against this repo's tree. By design it reports the retired-path entry as STALE, the never-reverified entry as AGING (other sample entries age into AGING too once their pinned dates fall outside the re-verification window), one skipped special path, and one dangling `obsoleted_by` pointer. The second runs the auditor's offline fixture tests.

## Adopting

Copy `conclusions_audit.py` anywhere in your repo (it takes the ledger path as an argument and resolves entry paths against `--root`), copy `capture_nudge.py` into `.claude/hooks/` and register it per [capture-nudge.md](capture-nudge.md), and add the one-line `.gitattributes` entry once your ledger has parallel writers. The auditor is a report, not a gate: it exits 0 whatever it finds, so it fits a scheduled job or a manual sweep without blocking anything. Its `--file-tasks` flag is a stub seam for wiring findings into your issue tracker.
