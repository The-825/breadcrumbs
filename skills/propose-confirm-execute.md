# Propose, confirm, execute

The moment an agent command touches a real account (mail, files, calendar, a CRM), the blast radius stops being your codebase and starts being your life. A code mistake is a revert. A mail mistake is a message someone already read, or a folder of things you cannot get back.

"Confirm before deleting" is the rule most teams write, and it is not enough on its own. It says nothing about batch size, nothing about which operation to reach for, and nothing about the outbound case where the damage is not deletion at all but a half-right message that actually sent. This is the fuller contract. Paste it into your agent rules file for any command that reaches a real account.

```markdown
## Account-touching command contract

Any command that operates on real mail, files, calendar, or records
follows propose, confirm, execute. It never acts autonomously.

1. Inventory first. Read and count before proposing anything. Report what
   is actually there.
2. Classify into named buckets (keep / duplicate / superseded / stray /
   misfiled, or whatever fits the domain). Every item lands in exactly one.
3. Propose in BATCHES, one table per action type. Never a single
   undifferentiated list of two hundred items, and never a plan that mixes
   a rename with a delete in one confirmation.
4. Execute only the batches explicitly confirmed, ONE batch at a time.
   Re-confirm between batches; approval of batch 1 is not approval of
   batch 2.
5. Unconfirmed batches are REPORTED AS PARKED, never silently dropped.
   The human should see what did not happen.
6. Always prefer the reversible operation: a recoverable trash over a hard
   delete, an archive over a purge, a label over an overwrite. State the
   reversibility window when there is one.
7. Do not wire the destructive tool at all. If the command has no
   legitimate need to hard-delete or to send, leave that tool out of its
   allowed-tools list entirely rather than instructing the agent not to
   use it.
8. Outbound messages are STAGED AS DRAFTS. The command has no send
   capability, by design, so the human sends.
9. Verify after execution: re-read the affected surface and report the
   observed end state, not the intended one.
```

## Adoption notes

Rule 7 is the one that separates this from a wish. Every other rule tells the agent how to behave; rule 7 changes what the agent is capable of. An agent that cannot reach a send endpoint cannot send the wrong thing at 2am no matter how the conversation went, and no prompt injection in a document it reads can talk it into an action it has no tool for. Where you can express the restriction as a missing capability instead of an instruction, do that.

Rule 5 exists because silent skipping is how trust dies. A human who confirms three of five batches should see the other two listed as parked, with a one-line reason. Otherwise the next run surprises them with work they thought was finished, or worse, they assume it was handled.

Rule 3 is a judgment call about batch size, and the honest guidance is to make batches small enough that a human can actually read the table. Twenty rows is reviewable, two hundred is a rubber stamp, and a rubber stamp is indistinguishable from no confirmation at all.

The point is not to make the agent slow. It is that the confirmation step should be the moment a human genuinely looks, which means the proposal has to be shaped so looking is cheap.
