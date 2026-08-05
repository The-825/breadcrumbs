# Write the threat model for your memory system, separately from the mechanics

> A documentation pattern, not a mechanism. Pairs with everything in
> `floating-memory.md` and `breadcrumbs-whitepaper.md`: those explain how the memory
> works. This is where you write down what it's defending against, so the two don't
> get tangled into one document that explains neither well.

## The problem

A doc that explains how a shared memory system works (the write path, the schema, the
decay rule) answers a different question than a doc that explains why it's shaped that
way. Mixing them produces a document that's too dense to onboard from and too vague to
audit against. The mechanics doc should read like a manual. The threat model should
read like a list of specific failure modes, each with the mechanism that answers it.

## The pattern

Name the failure modes first, as a fixed list, then map each to the mechanism that
answers it. Four failure modes cover most shared multi-agent memory systems:

- **Unauthorized leakage.** Something written to shared memory reaches a reader who
  shouldn't see it. Answered by whatever your access boundary actually is: a
  regulated-data fence, a secrets fence, a role check on read.
- **Stale propagation.** An entry that was true stays trusted after it stopped being
  true. Answered by expiry (a broadcast with a mandatory `until` date, per the
  floating-memory doc's NOTAM pattern) or by versioned acknowledgment (a session reads
  back which memory version it booted on, so staleness is visible rather than silent).
- **Contradiction persistence.** Two entries disagree and both stay live. Answered by
  supersession: nothing edited in place, a wrong entry killed by a newer one that
  names it, so the correction is on the record instead of a silent overwrite.
- **Provenance collapse.** A claim's origin gets lost, so a reader can't tell an
  oracle-verified fact from a model's guess. Answered by the trust ladder: every entry
  carries who or what asserted it and whether an independent oracle checked it, and
  unattributable claims are quarantined rather than trusted by default.

## The extraction boundary section

Close the threat model with an explicit line between what's portable and what never
leaves the system it was built for. State it as two lists: mechanisms and code that
generalize (the schema shape, the decay rule, the supersession logic), and anything
tied to one deployment that must never ship alongside them (domain-specific access
rules, real records, staff or user references, anything carrying an identifier). This
is the same discipline as a repo's own no-PII rule, applied one layer up, at the level
of what gets written about the system rather than what gets stored in it.

## Why write it separately

A reader auditing whether your memory system is safe to adopt doesn't want to reverse-
engineer your threat model from the mechanics doc's implementation details. A reader
learning to operate the system doesn't want the mechanics interrupted by defensive
reasoning. Two documents, two audiences, two jobs.
