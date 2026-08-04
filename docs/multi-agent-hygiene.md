# Multi-agent hygiene: several agents, one repo, no trampling

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

Running one agent against a repo is a discipline problem. Running several in parallel is a coordination problem, and the failure modes change: workers corrupt each other's checkouts, race each other to sequence numbers, launder second-hand instructions into direct ones, and conflict-storm the merge queue. Every rule below traces to a real failure in a production multi-agent setup. Adopt them before the second concurrent agent, not after the first collision.

## Isolate the working copies

**Builders get worktrees.** Two or more workers that each check out and edit a different branch in the same shared clone will corrupt long-running work: one worker's branch switch swaps the on-disk files under another worker's build or test run. Give every branch-editing worker its own git worktree (Claude Code's subagent tool supports worktree isolation as a launch option; plain `git worktree add` does the same by hand). Read-only workers may share a checkout, and a long-running verification should own the shared tree for its whole duration.

> **The failure this traces to.** One production team lost an hour-long end-to-end test run when a sibling worker switched branches in the shared clone mid-run, invalidating the tree under test. A later seven-worker wave was caught pre-push doing the same thrash. Worktree isolation ended the class.

**Scratchpads are private to their session.** A session's temp directory is per-container: a path written by one session is unreadable from another, even in the same project. Never hand another session a scratchpad path. Pass facts by inlining them in the message, committing them to a branch the receiver can fetch, or writing to a location that is genuinely shared. Within a single session's own worker fan-out, a shared scratchpad file is the right place for cross-worker facts, because those workers share the container; across sessions it silently does not exist on the other side.

## Partition file ownership per PR

Before a wave launches, the coordinator assigns each worker a disjoint file set, and the assignment is part of the brief: these files are yours, these are explicitly off-limits. Two builders editing the same file in the same wave is not a merge problem to solve later; it is a sequencing error to catch before launch. When two tasks genuinely need the same file, they are one task, or they run in sequence.

The same partitioning applies to *creating* files: workers pick non-colliding filenames from the brief, and anything that must slot into an existing shared surface waits for the follow-up.

## Serial resources get one writer

Some files cannot be partitioned and cannot merge mechanically: the shared index or catalog, README tables, ledgers where updates edit the same line, ordered prose docs. These are serial resources. In any parallel wave, each serial resource has exactly one designated owner, and every other worker routes its edit through the owner or lands it as a follow-up commit on top of the merged result. Parallel edits to a shared index are how a clean wave turns into an afternoon of conflict resolution.

Two structural helpers shrink the serial set:

- **Append-only ledgers can take a union merge.** Mark them `merge=union` in `.gitattributes` so both sides' appended lines survive a local merge with no hand edits. Know the honest limit: hosting platforms' PR mergeability checks may ignore merge attributes, so the PR can still show a conflict badge until the locally-merged branch is pushed. Never extend union merging to same-line-edit files; union duplicates those. The ledgers themselves are covered in [decision-capture.md](decision-capture.md).
- **Pre-assign identifiers.** Sequence numbers, migration numbers, catalog ids: the coordinator claims them centrally and hands each worker its numbers in the brief. Workers never self-claim from a shared counter in parallel; that race guarantees duplicate claims that someone must adjudicate later.

## Relayed rulings are attributed, then confirmed

In a multi-agent setup, operator decisions arrive second-hand: "the coordinator says the operator ruled X." Apply the ruling so work keeps moving, but keep its provenance visible: record and report it as relayed ("per the operator, via the coordinator"), never as something heard directly, and surface it for the operator to confirm at the next contact. A relay laundered into a direct instruction is unauditable, and relays do go wrong: in practice some arrive stale or garbled, so a cheap read-only verification of a relayed claim is worth running before building on it.

Coordination signals are the exception: lane ownership, stand-down orders, "session X owns that branch." Those come *from* the coordinator in its own authority and are honored directly. Only rulings that claim to speak for the operator carry the attribution-and-confirm requirement.

## Merge in waves: assembly line, not simultaneous

Build in parallel; merge serially. The wave pattern has three phases:

1. **Build.** Workers produce PRs on their own branches, in their own worktrees, against their assigned file sets.
2. **Verify adversarially.** Before anything merges, fresh eyes (a separate session or worker that did not write the code) try to refute each diff: undeclared references, scope drift, the change that breaks a sibling's assumption. The author checking their own work finds what they already believed.
3. **Merge in a controlled order.** One at a time, each on green. Every squash-merge re-dirties the open siblings, so re-clean between merges (update the next branch from main, resolve, re-verify) rather than firing everything at once and hoping. Evaluate each PR briefly before it goes: checks state, conflict state, whether anything changed since it was opened. Small same-concern PRs can consolidate into one merge to save CI cycles; unrelated concerns never fuse to save minutes.

Two conflict rules keep the queue moving:

- **Same-turn resolution.** A session that sees a conflicted PR resolves it in the same turn, on the feature branch (fetch main, merge, fix, run the cheapest covering check, push). A parked conflict compounds: every sibling that merges while it waits makes it worse.
- **Recurring classes get a structural fix.** The second time the same conflict shape appears, fix the class, not the instance: a union attribute, pre-assigned numbers, a single-writer rule, a retry on the transient base-branch-modified rejection. Hand-resolving the same race weekly is the failure this rule ends.

## One source of truth per fact

Every fact, figure, table, or procedure lives in exactly one canonical file; every other doc links there instead of copying. In a multi-agent repo this is load-bearing twice over: duplicated content is drift waiting for a continuity sweep to find, and it is also a conflict generator, because two workers updating two copies of the same fact produce a merge that no tool can resolve correctly. When you catch a worker (or yourself) pasting a table that exists elsewhere, replace the paste with a pointer.

## The fail-safe: flag, never guess

The rule that backstops all the others: anything borderline gets flagged, not guessed. A worker that hits unexpected file state, changes it did not make, a judgment call its brief did not settle, or an instruction that conflicts with the rules file stops and reports to the coordinator instead of resolving the ambiguity silently. This is also the standing instruction to put in every worker brief, because it is the one behavior that degrades gracefully: a flagged question costs one round trip; a guessed answer, multiplied by the parallelism, can cost the wave.

The same fail-safe governs publication-sensitive work: a worker unsure whether something is safe to include leaves it out and flags it. Omission is recoverable; the other direction sometimes is not.

## The starter version

Two concurrent agents are enough to need three of these rules on day one: worktrees per builder, a file-ownership line in each brief, and the flag-never-guess fail-safe. Add the serial-resource ownership rule the first time a shared index conflicts, and the full merge-wave discipline when the open-PR count regularly exceeds what one person reviews in a sitting. The rest of the operating shape these waves run inside (rules kernel, session handoffs, decision ledgers) is covered in [rules-spine.md](rules-spine.md) and [decision-capture.md](decision-capture.md).
