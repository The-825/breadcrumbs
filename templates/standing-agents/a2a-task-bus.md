# Agent-to-agent task bus

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

Work that one agent discovers for another dies in transcripts: an audit finds a rotten skill, the wake router names the desk that should care, and the finding evaporates when the session ends. The bus fixes the handoff by making every task a plain tracker issue with a small state machine on labels, so tasks are readable, searchable, and commentable in the views you already use. Use it the moment two agents (or one agent and future-you) need to hand work across a session boundary.

One issue per task. Title prefixed `[a2a]`, body opening with a fenced yaml block:

```yaml
from: "skills-gate"            # filing agent, or "session"
to: "desk-ops"                 # registry desk id the task routes to
task: "Re-point the deploy runbook reads: ops/runbook.md split in two"
context: "wake-routing digest, <date>"   # optional pointer
lease_hours: 24                # claim lease duration; default 24
source: "staleness gate"       # optional origin: a path, a PR, a run
authority: "G-YYYYMMDD-NN"     # optional: the standing grant the task acts under
```

The optional `authority:` field ties a task to a grant id in the authority ledger ([docs/authority-ledger.md](../../docs/authority-ledger.md)), so work handed across sessions carries its permission with it instead of re-asking or assuming.

## The state machine

Base label `a2a` on every task, plus exactly one state label. Routing label: `agent:<desk-id>`.

| State | Meaning | Enters via |
|---|---|---|
| `a2a:open` | unclaimed, available | file; lease-expiry revert |
| `a2a:claimed` | leased to an agent | claim |
| `a2a:blocked` | waiting on a dependency; reap ignores it | manual label swap |
| `a2a:dead` | unclaimed past SLA; escalated | reap |

Closing the issue is the completion signal. There is no done label; `complete` closes with a result comment, and that comment is the artifact the filer reads.

## The verbs

- **file**: open the issue with the yaml body; label it `a2a` + `a2a:open` + `agent:<desk-id>`.
- **claim**: swap `a2a:open` for `a2a:claimed`; comment the claiming agent and the lease expiry ("Lease expires <timestamp>").
- **complete**: close the issue with a result comment.
- **renew**: comment a fresh expiry; the latest expiry comment is authoritative.
- **list**: table the open tasks, filterable by state and by desk.
- **reap**: enforce the two decay rules below. Dry-run by default; an explicit apply flag acts.

## Leases and reaping

Claims decay so a crashed or distracted agent cannot hold work forever. Reap applies two rules:

1. A claim past its lease expiry reverts to `a2a:open` with a comment. A claim whose expiry comment is missing or malformed falls back to last activity plus the default lease, so a broken claim still cannot squat.
2. An open task with no activity past the SLA (a week is a sane default) becomes `a2a:dead` with an escalation note for the operator's digest. Dead means "the fleet dropped this"; a human decides whether it mattered.

## Why issue-backed

Because the hard part of a task bus is not transport, it is visibility and audit, and your tracker already solved both. Any tracker with ids, labels, and comments works: the states are labels, the lease is a comment, done is closed. You inherit search, notifications, and permalinks for free, and a human can intervene in any task with tools they already know.

## The script

The reference implementation this page generalizes runs about six hundred lines of stdlib Python against one tracker's API: label auto-creation, expiry parsing, an offline selftest for the state machine. That does not compress honestly into a snippet, and yours is an afternoon against your own tracker: six verbs, each one or two API calls plus a label swap. Two build notes worth stealing: keep every decision (which label, whether a lease expired) a pure function so a selftest runs with no network, and auto-create missing labels idempotently on first use so setup is nothing.

File what you cannot finish. An unfinished tail filed on the bus is fleet memory; one left in a transcript is gone.
