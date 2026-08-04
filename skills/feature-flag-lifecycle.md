# Feature flag lifecycle

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

Shipping a feature to everyone at once leaves you one bad deploy away from a pressure revert: a rollback commit written at speed, entangled with unrelated changes that landed since, pushed while users are already seeing the breakage. The alternative is a graduation ladder. Every user-visible feature merges dark behind a flag, and rollout becomes a config change instead of a deploy. Paste the rules below into your agent rules file or engineering handbook.

```markdown
## Feature flag rules

1. Every user-visible feature ships behind a feature flag, default OFF
   in production. The code merges and deploys dark.
2. Graduation ladder, in order:
   a. OFF: merged, live in production code, invisible to everyone.
   b. Owner-only preview: enabled for the builder's own account, who
      exercises the feature against real production data while nobody
      else sees it.
   c. Role or team pilot: enabled for one role or team.
   d. Graduated: default ON for everyone.
3. Rollback at any rung is a config change: reset the flag to OFF and
   clear the per-identity and per-role enables. No deploy, no revert.
   Reversible by config, not by revert.
4. Flags fail closed. If the flag store is unreachable or the flag is
   unknown, the feature is OFF.
5. The flag store lives on the transactional database, not the
   analytics warehouse. A warehouse-backed flag table becomes a stale
   second source of truth.
6. Retire the flag once the feature has been graduated and stable for a
   full release cycle. Remove the flag check and the flag row; a dead
   flag is a trap for the next reader.
```

## The subtraction review

A flag review that only asks "what should we flip next" grows the flag set forever. Give the periodic review a subtraction section: any flag that has been default-ON for a full cycle with no incident and no plausible rollback story is a candidate to DELETE (remove the flag, keep the code), and any flag that has sat default-OFF with no activation plan is a candidate to delete along with its code. Every surviving flag is a branch both humans and agents pay to reason about on every read; a flag that can never meaningfully be OFF again is dead weight wearing a safety vest.

### Widen it past flags

Flags are just the easiest thing to count. The same review, on the same cadence, should sweep four candidate classes, because they all rot the same way and the review has already paid the cost of pulling the data:

- **Flags** that are permanently ON or indefinitely OFF, as above.
- **Orphaned surfaces:** a page, panel, or route whose gate resolves off for every user. It still ships, still gets read, still confuses the next person.
- **Superseded documents:** design docs and plans a later decision replaced. The successor exists; the original is still the first search hit.
- **Uninvoked commands and skills:** anything with no recorded use since the previous review.

Three rules keep it safe. **Evidence per item, never age alone:** a candidate needs a named superseding artifact or a measured absence of use, because "this looks old" is how live things get deleted. **The reviewer proposes and removes nothing:** subtraction is a human decision, and the review's output is a ranked list. And the honest one, **an unmeasurable item is a named evidence gap, not a fabricated zero:** if you cannot tell whether a command has been used, the row says "no usage data available" rather than "0 uses", because a confident zero is exactly what gets something deleted.

The cadence answer is that this rides along with a review you already run. It reuses data you already pulled, so it costs almost nothing beyond the reading.

## Adoption notes

The binding rule is only the first hop: ship OFF. Every later hop is a judgment call the owner makes when ready, which is exactly the point. The ladder separates "is the code deployed" from "who can see it", and once those are separate questions, launches stop being events.

The owner-only rung earns its keep fast. It is the only way to test a feature against real production data with zero user exposure, which matters most for anything that writes: a staging box that shares the production database cannot give you that safety, because a staging write is a production write.

On storage, the failure mode is subtle. A flag table in the analytics warehouse looks convenient right up until runtime toggles and the warehouse copy drift apart, and then two systems disagree about what is live. Keep flags where your app already does transactional reads, and treat the runtime store as the single source of truth.

When in doubt: flag it.
