# The issue-backed task bus

> **Pattern only. The CLI described here does not ship in this kit.** It is roughly six
> hundred lines against your own issue tracker's API and does not compress into a
> snippet, so what follows is the contract it has to satisfy and the failure modes it
> has to survive. `templates/standing-agents/a2a-task-bus.md` covers the same ground
> from the fleet side.

## The problem

Several agent sessions, or several people plus agents, need a shared queue of
in-progress work: what's claimed, what's blocked, what's dead. A database is
overkill for this. A doc that gets hand-edited by multiple writers is a merge
conflict waiting to happen.

## The pattern

Use GitHub issues as the queue. Issues already give you a title, a body, comments,
and labels for free, and GitHub already serializes writes to them, so you get a
lockable record without building one.

- **Labels are the state machine.** `open`, `claimed`, `blocked`, `dead`, whatever
  states your work actually has. A worker claims a task by moving the label and
  leaving a claim comment naming itself and a timestamp, nothing more.
- **Leases expire.** A claim carries a lease window (an hour, a day, whatever fits
  your task grain). A worker that goes silent past its lease releases the claim
  automatically on the next sweep, so a crashed session doesn't permanently starve a
  task.
- **A small CLI, not a service.** File, claim, renew, complete, list, and reap are
  the whole verb set. Each is a thin wrapper over the GitHub issues API. No server to
  run, no new credential to manage beyond the one your agents already have.
- **Comments are the audit trail.** Every claim, renewal, and completion leaves a
  comment. You get a free history of who worked what and when, readable by a human
  in the GitHub UI without touching the CLI.

## Why not a database

A database needs a schema, a host, a migration path, and a reason to trust it stays
up while an agent session is mid-task. Issues need none of that, and the audit trail
you'd have to build by hand in a database, you get by default here. The tradeoff is
throughput: this pattern is for dozens of tasks a day, not thousands a second. If
you're past that scale, you've outgrown the pattern and should reach for a real
queue.

## Adopting it

1. Pick your label set and write it down (a short `TASK_BUS.md` in your repo works).
2. Write the CLI verbs as thin GitHub API wrappers, `file` / `claim` / `renew` /
   `complete` / `list` / `reap`.
3. Give every agent session the CLI and the instruction to check the bus before
   starting work and file what it finds before finishing.
4. Run `reap` on a schedule (a cron workflow, or a step at the top of each session)
   so expired claims don't rot.
