# SESSION_STATE.md template

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

Sessions die. They hit context limits and compact, they get closed mid-task, they get picked up the next morning by a different agent on a different model. In-flight state that lives only in a transcript is gone the moment any of that happens, and the next session either re-derives it (slow, error-prone) or trusts a lossy auto-summary. The fix is a living handoff file at repo root, refreshed on an explicit trigger: the operator says "checkpoint" and the agent rewrites this file to reflect where things actually stand.

Two properties make it work. It is rolling and short by design (not a changelog, not a roadmap, only what is in flight, decided, or blocked right now), and the refresh is event-driven, so it happens before a risky handoff instead of never.

## The template

```markdown
# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out to the changelog so
> this file never grows into a log. Durable rules belong in CLAUDE.md, durable
> rulings in DECISIONS.md; this file holds only the rolling state.

Last refreshed: <date> by <session/model>

## Current state

- Active branch: <branch name>
- Open PR: <number + title, or "none">
- In-flight, uncommitted edits:
  - `<file path>`: <what is half-done in it, one line>
  - `<file path>`: <what is half-done in it, one line>

## Next steps (in order)

1. <the very next action, specific enough to execute cold>
2. <then this>
3. <then this>

## Pending decisions (awaiting the operator)

- <question that blocks work, phrased so a yes/no or a pointer unblocks it>

## Standing instructions for the next session

- <transient operator preferences for this stretch of work; durable rules go
  to CLAUDE.md instead>

## Irreplaceable exact values

> Reserved for values that cannot be re-derived from the repo: IDs, hashes,
> one-off command outputs, exact config values. A compaction or summary must
> preserve this section verbatim.

- <name>: <exact value>

## Recently landed (rolling, keep the last handful)

- <date>: <what merged or shipped, one line>
```

## Adoption notes

Name the trigger word with your operator and treat it as a contract: "checkpoint" means rewrite the whole file, not append to it. Checkpoint before any model or agent switch so the next one boots from written state instead of a summary. The irreplaceable-values section earns its place the first time a compaction eats a job ID you needed; naming the section lets you tell any summarizer to keep it word for word.

Keep it current, keep it short. A stale handoff is worse than none, because the next session will trust it.
