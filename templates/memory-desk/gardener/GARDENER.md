# GARDENER.md · the desk's curation contract

> Assumes: the desk lives at `memory/` in a git repo, changes land through
> pull requests, and a merge waits for a human approval label. The pass can be
> run by a scheduled agent or by a person; the contract is the same.

The desk works because writing to it is cheap: any session appends a raw
journal line in one command and moves on. The price of a cheap write path is
that somebody must curate, and "somebody, sometime" is how ledgers rot. This
file makes curation a scheduled job with a fixed contract instead of a
goodwill activity.

Cadence: weekly, or on demand when the journal grows noisy. The companion
workflow template ([gardener.yml](gardener.yml)) opens an issue when entries
are waiting, so the work arrives instead of waiting to be remembered.

## Inputs

- `memory/journal.jsonl`: every entry newer than the last gardening marker
- `memory/index.tsv`: the current rows
- `memory/MEMORY.md`: the kernel, for the size check only

## The pass, in order

1. **Promote.** For each journal entry that states a durable fact, ruling, or
   gotcha: write an index row. Key it the way the entry was asked for (the
   `key` field, when present, is how a session actually phrased the miss, so
   it is the best alias you will ever get). Point `source` at where the fact
   lives or was proven; set `checked` to today. Entries typed `todo` or
   `state` are not facts; route them to the repo's task or handoff surface.
   `python3 gardener/promote.py --apply` does this step mechanically. It reads
   `tombstones.tsv` before proposing rows and refuses a normalized key-and-answer
   pair that was already rejected, so retained source material cannot launder a
   known-wrong value back through gardening.
   Possible semantic duplicates are appended to
   `consolidation-proposals.jsonl` as stable pending proposals that preserve
   both rows. A proposal is a review surface, not permission to merge.
   including the exact-key half of dedupe (step 2 below) and running
   `mem check`; it flags anything needing judgment (a derived key, a
   possible semantic duplicate) instead of guessing, and it writes nothing
   on `--dry-run` (the default). It does NOT do steps 3-5, those stay
   human calls, same as before.
2. **Dedupe.** A new fact that restates an existing row updates that row
   (answer, source, checked date) rather than adding a twin. `mem check`
   catches literal key collisions; you catch semantic ones.
3. **Refresh.** For rows past the stale horizon (mem prints the flag), re-read
   the source. Still true: bump `checked`. Changed: fix the answer. Gone:
   retire the row. `memory/mem recheck` narrows this queue for you: it lists
   the rows whose source actually moved since the row was last checked, which
   is a much shorter list than everything the calendar calls aging. It reports
   suspicion, never a verdict, so the re-read is still yours.
4. **Retire, never silently.** Use `memory/mem reject "<key>" --reason "<why>"`
   rather than deleting the line by hand. It removes the row, records the
   retired answer in `tombstones.tsv`, and journals the correction, which means
   `mem check` will fail if that same answer ever comes back under that key. A
   different answer for the same key passes, because that is a correction and
   correcting is the point. The reason is mandatory: a tombstone with no reason
   is just a deletion. List the retirement in the PR body too. Deleting a fact
   is a reviewed act, not a side effect.
5. **Trim the kernel.** If `MEMORY.md` is near its line cap, move anything
   that answers a question into a row. The floor section is not yours to
   touch: it is frozen, test-pinned, and edited only by the operator.
6. **Verify.** Run `memory/mem check` and the desk's tests. A gardening PR
   that fails its own integrity gate does not go up.
7. **Mark.** Append the watermark to the journal, after everything else:
   `memory/mem add "gardened through <newest ts processed>" --type state`
   The next pass starts after this marker, so nothing is processed twice.

## Boundaries

- Append-only journal: the pass never rewrites or deletes journal lines.
- The floor in `MEMORY.md` is out of scope, always.
- Everything lands as one PR that waits for the approval label. The gardener
  proposes; a human merges.
