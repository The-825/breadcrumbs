# Self-audit against the Agent Memory Atlas rubric

Pinned to `a1886de` (main, 2026-08-12). Methodology borrowed directly from
[neoneye.github.io/agent-memory-atlas](https://neoneye.github.io/agent-memory-atlas/):
seven mechanisms (capture, extraction, storage, retrieval, correction,
forgetting, trust), evaluated by inspecting concrete schemas and tests,
tracing data through its full lifecycle, separating product claims from
visible code from committed evidence, and pinning every claim to a commit
so it stays auditable. This is a self-review, not an external one; read it
with that bias in mind, and check the cited line numbers rather than the
prose.

**Assumes:** you've read `templates/ledger-tools/memory_engine.py` and
`templates/memory-desk/mem`, or are willing to open them alongside this.

## The finding, stated first

The atlas's central claim is "retrieval is only half the memory problem."
This repo has two memory subsystems built at different times with
different postures on the other half: `memory_engine.py` (the ledger-tools
kit) treats correction and forgetting as first-class, tombstones and
supersession are load-bearing. `mem` (the memory-desk kit) treats capture
and retrieval as first-class and defers correction to a human-run gardener
pass. Neither is wrong; they're solving different problems at different
scales. But a reader who only skims the README could mistake one kit's
strength for the whole repo's, which is a documentation gap this audit
surfaces on its own.

## Mechanism by mechanism

**1. Capture: strong, evidence-preserving in both kits.**
`mem add` (`templates/memory-desk/mem:170-206`) appends a raw journal
entry, timestamped, typed, with an optional source, before any processing.
`memory_engine.py`'s `store_fact()` records status `asserted`, never
`verified`, on write (`memory_engine.py:165-217`), the same raw-before-
processed discipline the atlas rubric asks for. Evidence: both write paths
are append-first; neither mutates existing state to capture a new fact.

**2. Extraction: the weaker of the two kits is `mem`'s.**
`memory_engine.py` has no extraction step at all, callers write structured
facts directly; there's nothing raw to extract FROM. `mem`'s journal is
raw text, and promotion to the queryable `index.tsv` is described as a
"gardener pass" (`mem:206`, `gardener/GARDENER.md`) but the gardener
itself ships as a markdown runbook, not executable code, in this
repo, `templates/memory-desk/gardener/` contains `GARDENER.md` and
`gardener.yml` only. That's a real gap: the promotion step the tool's own
help text promises ("the gardener promotes durable entries to index.tsv on
its next pass") has no committed implementation to inspect. Separating
claim from code per the atlas's own discipline: this is a documented
intent, not yet a checkable mechanism.

**3. Storage: schema-explicit, versioned, both kits.**
`memory_engine.py` facts carry `value`, `status`, `evidence`,
`recorded_at`, `scope`, optional `valid_from`/`valid_until`
(`memory_engine.py:212-221`). `mem`'s `index.tsv` is a flat, greppable,
git-diffable table (`mem` docstring + `MEMORY_TEMPLATE.md`). Both are
plain text under version control, no opaque store, no vector index hiding
what's in it. This is the strongest mechanism in the repo by the atlas's
own standard: a store you can `git blame`.

**4. Retrieval: has a real regression test, which the atlas explicitly
values.** `retrieval_exam.py`'s `run_forbidden_check()`
(`retrieval_exam.py:265`) replays the boot matcher against a set of probes
to catch entries that should be superseded but still win an injection
slot, exactly the "descent problem" the atlas methodology names as the
part most systems skip. `memory_engine.py`'s `build_context()` composes
recency, keyword overlap, and three filter axes (as-of, valid-at,
audience) deterministically, no vector search, no paraphrase matching,
and says so in its own output header. Honest about its limits, which the
atlas rubric rewards more than an unstated one.

**5. Correction: the sharpest asymmetry between the two kits.**
`memory_engine.py` has `store_fact()`'s supersession discipline (the prior
value and status are logged to the episodic ledger before an overwrite,
`memory_engine.py:198-210`), `reject_fact()`'s tombstones (a rejected
value can't be silently re-asserted, `memory_engine.py:224-249`), and,
as of the 2026-08-12 fix, `verified_at` distinct from `recorded_at` so a
correction's timing survives replay (`memory_engine.py:288-330`, the
Atlas review's own prior finding, now closed). `mem` has no equivalent:
`conclusions_audit.py` flags STALE (path no longer exists) and AGING
(unchecked past the ledger's own adaptive horizon, `mem:adaptive_stale_days()`,
30-90 days depending on re-check cadence) entries, but flagging is not
correcting, a human still has to act on the flag. This is the real gap
this audit found: `mem`'s correction path is entirely human-driven, no
automated re-verification, no tombstone equivalent.

**6. Forgetting: deliberately different postures, both defensible.**
`mem`'s journal is explicitly append-only forever
(`gardener/GARDENER.md:50`: "the pass never rewrites or deletes journal
lines"). `memory_engine.py` has real deletion paths: `reject_fact()`
removes a live entry from `facts.json` (keeping the tombstone and an
episode as the record of why), and the sibling `memory_gardener.py` (in
the ucr-honors consuming repo, not this one) implements the
mechanically-dead-only auto-archive class this kit's docs describe but
don't ship code for here. Separating claim from code again: `mem`'s
"nothing forgotten" is fully implemented; `memory_engine.py`'s "verified
deletion is appropriate" is implemented for facts, described but not
executable for the ledger-scale gardener pattern this repo's own
`templates/memory-desk/gardener/GARDENER.md` documents.

**7. Trust: closed the atlas's own named gap, worth stating plainly.**
The atlas's prior review of this repo (before this fix) named trust-axis
blindness as its sharpest finding: an as-of replay checked only when a
fact was recorded, never when it was verified. `verify_fact()` now stamps
`verified_at` and `build_context()`'s as-of replay masks verified status
to asserted when verification postdates the cutoff or is missing
(`memory_engine.py:379-390`), read-time only, storage untouched. A soft
backfill (`backfill_verified_at()`, `memory_engine.py:243-263`) protects
pre-fix ledgers from an unearned trust regression. 12 selftests cover it.
This is the one mechanism where "we fixed the atlas's own finding" is a
checkable, cited claim, not a self-assessment.

## What this audit would tell an external reviewer to look at next

Two concrete gaps, stated the way the atlas states its own findings, as
something to inspect and trace, not something to take on faith:

1. **The gardener promotion step has no committed code.** `mem`'s help
   text promises index promotion "on its next pass"; nothing in
   `templates/memory-desk/gardener/` executes it. Either ship the
   promotion script or reword the help text to say it's a manual step
   until it does.
2. **`mem` has no correction mechanism, only a staleness flag.** A fact
   that's wrong but not yet past its adaptive horizon (30-90 days,
   `mem:adaptive_stale_days()`) surfaces nowhere; `conclusions_
   audit.py`'s AGING/STALE split is a forgetting-adjacent check, not a
   correction one. Whether this matters depends on scale: at
   single-operator, hand-curated volume (this kit's stated design point,
   `docs/`'s own framing) a human catching it in normal use may be
   sufficient. At any volume beyond that, it's a real gap.

## Follow-up
- CONCLUSIONS-equivalent for this repo: `planning/DECISIONS.md`, a ruling
  entry if Jovan wants to record a decision from this audit (e.g., whether
  to build the gardener promotion script or reword the claim).
- No code changed by this audit; it's read-only inspection, per the
  atlas's own methodology.
