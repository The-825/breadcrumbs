---
description: Serial merge driver for a wave of open PRs - evaluate each against its stated scope, consolidate compatible small ones, keep every PR mergeable in order, and let the automerge gate land them one after another. Never merges by hand.
argument-hint: "[PR numbers in intended order, or 'all' for every open agent PR]"
allowed-tools: Bash, Read, Grep
---

Land the wave **$ARGUMENTS** as an assembly line, not a simultaneous dump.
The gate (your automerge workflow) owns every merge; this command's whole
job is to make each PR mergeable, in order, and let the gate complete.
`/land` shepherds one PR; this sequences a wave of them.

The doctrine, from the production setup this comes from: "merge all N"
never means simultaneously. Evaluate each, order them, and consider which
small PRs can ride together, because every PR event burns a full check
set.

## Step 1: inventory and order

List the wave's PRs. For each capture: base, head, checks state, mergeable
state, protected-path exposure, label state. Order cheapest-first unless
the operator gave an order: docs before code, independent before
dependent.

## Step 2: evaluate each PR against its stated scope before it goes

Re-read the diff against the PR body's Summary and What's-NOT-in-scope. A
PR whose diff drifted from its description (stray files, a second concern,
stale against its base) gets fixed or re-described BEFORE it merges, not
discovered after.

## Step 3: consolidate where it saves CI time

Small, compatible, same-concern PRs combine into one bigger merge instead
of burning a check set each: merge the sibling branches into one head,
close the others with a pointer comment. Never force-fuse unrelated
concerns; one coherent concern per merge still governs.

## Step 4: work the train, one PR at a time

For the current PR:

- **Zero check runs** on the head SHA: push an empty commit to fire CI
  (`git commit --allow-empty -m "ci: fire checks"`, push).
- **Conflict**: resolve on the feature branch, same turn: fetch the base,
  merge it in, fix, push. Never resolve by hand-merging the PR.
- **Looks green but sits unmerged**: list the head SHA's check runs. A
  superseded run's `cancelled` pinned next to a newer `success` of the
  same name poisons a gate that judges all runs; the kit gate dedups to
  the newest run per name (AUTOMERGE_GOTCHAS.md, gotcha 11), and the
  unstick move either way is an empty commit for a fresh SHA.
- A green unmerged PR may also be label-waiting by design (protected
  paths, rung one). Say so and move to the next car rather than stalling
  the train.

## Step 5: between merges

Re-fetch the base (cached refs go stale in minutes) and re-clean the next
sibling: each squash-merge re-dirties the branches still in line, so the
next PR gets the base merged in before its turn.

End with one table: PR, verdict (merged / waiting-on-label / fixed-and-
queued / consolidated-into), and anything the operator must release.
