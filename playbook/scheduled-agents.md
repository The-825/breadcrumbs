# Scheduled headless agents

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

The [doc-sync agent](doc-sync-agent.md) is one member of a family: agents that run on a
schedule, headless, with no human in the loop while they work. That last clause is the
design constraint for the whole family. When nobody is watching, authority gets
designed down, not up: every archetype below produces drafts a human reviews, none can
merge or send anything, and each one's toolset simply lacks the dangerous verbs rather
than being asked nicely not to use them.

Three archetypes have earned their keep in production. Each sketch is the generalized
shape, not runnable workflow YAML; the doc-sync page shows what a full workflow file in
this style looks like.

## Archetype 1: the self-healing janitor

Fixes mechanical breakage, and only mechanical breakage. The trigger is a cheap
deterministic check (parse every source file, validate every config); the agent runs
only when that check is red, applies the minimal fix, and the workflow opens a draft PR
the agent can never merge.

```text
schedule: weekly cron + manual dispatch
permissions: write a branch, open a PR, nothing wider
bounded: a hard timeout caps the failure path

1. Run the deterministic check over the tree. Green: exit, no agent run.
2. Red: run the headless agent with a minimal-fix contract:
   fix the breakage, verify with the SAME check, no refactoring,
   no renames, nothing beyond restoring the original intent.
3. Tree changed: open a DRAFT pull request on a dedicated fix branch,
   with the failing check's output and a review checklist in the body.
4. Tree unchanged: report and exit. The agent never merges anything.
```

Two properties carry it. The deterministic check is both the trigger and the verifier,
so the agent cannot declare success on its own judgment. And loop prevention is
structural: a merged fix passes the check, so the next scheduled run does nothing.
Cadence is a cost decision; when your PR gates already block this failure class before
merge, the janitor is a weekly backstop for what slips through, not a per-push fixture.

## Archetype 2: the overnight sweeper

Reads pipeline state while you sleep and stages a briefing for the morning. It sweeps
its sources (open PRs and CI state, data-pipeline freshness markers, service health),
appends a dated section to an append-only open-loops ledger, and stages the briefing as
a draft. It has no send tool, by design: the reliable way to guarantee an agent never
sends on your behalf is a toolset in which send does not exist.

```text
schedule: daily cron, pre-workday, staggered off :00
permissions: read everything it sweeps, write nothing in the repo

1. Sweep each source; note per-source freshness against expectations.
2. Append ONE dated section to the open-loops ledger (append-only:
   prior sections are never edited, so the ledger is its own audit log).
3. Stage the morning briefing as a DRAFT for the operator to read,
   edit, and send or discard. No send capability exists in the toolset.
4. Degrade, never die: one unreachable source becomes a one-line
   degradation note in the briefing, and the rest of the sweep runs.
5. A post-run guard fails the job if the repo tree is dirty; this
   agent has no legitimate repo writes.
```

The degradation rule matters more than it looks. A sweeper that hard-fails when one
source is down delivers nothing on exactly the mornings something is wrong, which is
when the briefing is worth the most.

## Archetype 3: the weekly triage router

Reads the week's accumulated findings and routes every one to an owner. It sweeps the
triage sources (the issue inbox, error-class log entries, dead letters on the task
queue, new flake-ledger rows), files or refreshes a task entry per finding, and fixes
nothing. A clean week is a one-line all-clear.

```text
schedule: weekly cron, pre-workday, clear of the sweeper's slot
permissions: read the sources; write task entries only

1. Sweep each triage source for the trailing week.
2. Every finding becomes a filed or refreshed task entry pointing at
   its owner, with the evidence attached. Duplicates refresh the
   existing entry rather than filing a second one.
3. Fix NOTHING, even the one-line fixes. Route only.
4. Stage a short weekly summary as a draft; a clean week is one line.
```

The fix-nothing rule is what separates a router from a loose cannon. An agent that
routes and fixes will fix whatever it happens to understand and silently drop what it
does not, which converts triage coverage into triage roulette. Routing is the whole
job; the fixes happen in reviewed PRs owned by whoever the finding was routed to.

## The shared safety posture

Every archetype, same floor:

- **Draft-only outputs.** PRs open as drafts, messages are staged as drafts. A human
  promotes or discards; the agent's work product is always a proposal.
- **No merge or send authority, by toolset.** The dangerous verb is absent, not
  forbidden. Absence survives prompt injection, bad instructions, and model error;
  prohibition survives none of them.
- **Append-only dated state.** Ledgers and logs grow by dated sections and are never
  rewritten, so every run is auditable after the fact and a re-run is detectable
  (today's section already exists) instead of duplicative.
- **Idempotent runs.** Re-running against the same state produces no second copy of
  anything: check for today's section, today's draft, an existing task entry before
  writing.
- **Least privilege per archetype.** The janitor alone gets branch-write; the sweeper
  and router run read-only against the repo with a post-run dirty-tree guard that
  fails the job if the tree changed.
- **Bounded and staggered.** Hard timeouts cap the failure path where a stuck agent
  burns a runner and tokens; schedules stagger off :00 and off each other so runs
  never contend.
- **A smoke mode.** Manual dispatch defaults to probe-only (touch each source, write
  nothing, print an all-clear), so you can verify wiring without a full run.

Adopt in risk order: sweeper first (pure reads, teaches you the degradation and
idempotency habits), router second (writes task entries only), janitor last (writes
code, still draft-gated). The doc-sync agent slots in beside them as the fourth member,
and the merge gate all their PRs eventually face is the label-gated automerge in
[ci-kit/workflows/](../ci-kit/workflows/AUTOMERGE_GOTCHAS.md).
