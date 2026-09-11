# SESSION_STATE.md template

Sessions die. They hit context limits and compact, they get closed mid-task, they get picked up the next morning by a different agent on a different model. In-flight state that lives only in a transcript is gone the moment any of that happens, and the next session either re-derives it (slow, error-prone) or trusts a lossy auto-summary. The fix is a living handoff file at repo root, refreshed on an explicit trigger: the operator says "checkpoint" and the agent rewrites this file to reflect where things actually stand.

Two properties make it work. It is rolling and short by design (not a changelog, not a roadmap, only what is in flight, decided, or blocked right now), and the refresh is event-driven, so it happens before a risky handoff instead of never.

## The template

```markdown
# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out to the changelog so
> this file never grows into a log. Durable rules belong in CLAUDE.md, durable
> rulings in DECISIONS.md; this file holds only the rolling state.

Last refreshed: <date and timezone> by <agent>
Checkpoint status: <verified | partly verified | unverified>
Owning repository and directory: <owner/repo and bounded path>
Source revisions: <base commit, branch HEAD, PR head if any>

## Current state

- Active branch: <branch name>
- Open PR: <number + title, or "none">
- PR head and checks: <head SHA + pending/passing/failing/unknown>
- Review and merge: <pending/approved/merged/unknown, with evidence>
- Deployment: <separate deployed/pending/not applicable/unknown state>
- In-flight, uncommitted edits:
  - `<file path>`: <what is half-done in it, one line>
  - `<file path>`: <what is half-done in it, one line>

## Next steps (in order)

1. <the very next action, specific enough to execute cold>
2. <then this>
3. <then this>

## Decisions, corrections, and supersession

- <decision or correction>: <source and observed time>; supersedes <prior claim
  or "nothing">

## Failures and workarounds

- Failure <id>: action=<attempt>; observation=<direct evidence>; known cause=<or
  unknown>; suspected cause=<or none>; side effects=<or none>; blocker=<or none>;
  next action=<specific step>
- Workaround for <failure id>: rationale=<why safe>; checks=<evidence>; residual
  limits=<what remains unverified>

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

## Assumptions and evidence validity

- <evidence>: valid while <source revision and assumption>; invalidate when
  <material change>

## Recently landed (rolling, keep the last handful)

- <date>: <what merged or shipped, one line>

## Unfinished work

- <item>: owner=<person or agent>; state=<pending or blocked>; next=<executable
  action>; evidence needed=<completion proof>
```

## Adoption notes

Name the trigger word with your operator and treat it as a contract: "checkpoint" means rewrite the current projection, not append to it. Preserve prior decisions by linking their source and marking supersession. Checkpoint before any model or agent switch so the next one boots from written state instead of a summary. A changed PR head invalidates old checks, and pending CI or review stays in the checkpoint. The irreplaceable-values section earns its place the first time a compaction eats a job ID you needed; naming the section lets you tell any summarizer to keep it word for word.

Keep it current and short. A fresh session still verifies the repository, branch,
worktree, sources, and PR before trusting it. Old memory is context, not authority.
