# Incident postmortem template

Outages happen. What separates a setup that improves from one that repeats itself is whether each incident leaves a written record: what broke, what it cost, what fixed it, and, the part most postmortems skip, where the diagnosis went WRONG along the way. Keep the records as dated files in one directory (`INCIDENTS/` or `docs/incidents/`, filename `YYYY-MM-DD-<slug>.md`), written while the evidence is still fresh, never deleted.

The load-bearing section is **Misdiagnosis lessons**. Real incidents burn most of their hours on confident wrong theories, and those wrong turns are invisible in a root-cause-only writeup. Recording what was believed, what the evidence actually supported, and what check would have caught it sooner is what makes the NEXT incident shorter. Be honest there; the section only works if it names the wrong turns plainly.

One file can cover several co-occurring incidents (a bad day often stacks them); give each its own root-cause section and keep one shared timeline.

## The template

```markdown
# Incident postmortem: <YYYY-MM-DD> <short name>

**Date:** <YYYY-MM-DD>
**Status:** <open | mitigated, follow-ups pending | resolved>
**Severity:** <who was affected, how completely, for how long. One line.>

## Summary

<Three to six sentences: what broke, what caused it, what the user-visible effect
was, how it was fixed, and how long it lasted. Written so someone who was not
there gets the whole story before the detail.>

## Timeline (UTC)

| Time | Event |
|---|---|
| <hh:mm> | <what happened, with the evidence source: log line, deploy run, message> |
| <hh:mm> | <first detection: who noticed, how> |
| <hh:mm> | <diagnosis milestones, including the wrong turns> |
| <hh:mm> | <fix merged / deployed / verified> |

## User impact

- **<affected group>:** <what they could not do, from when to when>
- **<data or pipeline impact>:** <what went stale or was missed, and whether it
  backfilled>
- **<tooling or CI impact>:** <what internal capability was degraded>

## Incident <n>: <name>

<One section per distinct incident in the window. For a single incident, keep one
section; the structure is the same.>

**Root cause.** <The actual mechanism, stated plainly. Name the triggering change
or event, not just the failing component.>

**Why monitoring missed it.** <What check existed, what it actually verified, and
the gap between that and the failure mode. "No check existed" is a valid answer
and a follow-up.>

**Fix.** <The change that resolved it: PR or commit ref, when it took effect.>

**Verification.** <The observation that proved recovery: the passing request, the
matching log line, the advanced watermark. Absence of complaints is not
verification.>

## Misdiagnosis lessons (be honest, these cost hours)

<One entry per wrong turn taken during diagnosis.>

- **What was believed:** <the theory held at the time, and why it seemed to fit>
- **What the evidence actually supported:** <the reading of the same evidence that
  turned out to be right, or the evidence that was available but not consulted>
- **What check would have caught it sooner:** <the specific query, log filter, or
  test that would have falsified the wrong theory in minutes>

## Open follow-ups

- [ ] <follow-up action> (owner: <who>, tracked in: <issue/PR link>)
- [ ] <monitoring or guard gap to close>

<Close-out habit: when the follow-ups land, add a dated verification note here
(or a short companion file) confirming each one actually shipped. A follow-up
list nobody re-checks is where postmortem value goes to die.>
```

## Adoption notes

- **Write it within a day or two.** The misdiagnosis section decays fastest; a week later everyone remembers the clean story, not the wrong turns.
- **Timeline entries cite evidence.** Every row should name where the timestamp came from (a log line, a deploy run, a message). A timeline from memory is a narrative, not a record.
- **Blameless, but specific.** Name the change and the mechanism, not the person's judgment. "The config change on <date> altered X while the service still expected Y" is specific and blameless at once.
- **Pair with the `/incident` command** (in this kit's command set) if you install it: the command handles live triage and rollback, and its close-out step points here for the writeup.
- **Status stays current.** An incident with pending follow-ups is "mitigated, follow-ups pending" until the verification note lands, and the file is the one place that tracks that honestly.
