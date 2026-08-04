# Autonomous discovery scouting

> Companion to `doc-sync-agent.md` and `scheduled-agents.md`: another standing agent
> family, this one pointed outward at the ecosystem instead of inward at your own repo.

## The problem

You want an agent that keeps an eye on what's new in some space (tools, libraries,
competitors, research) and tells you what's worth a look. The naive version either
costs nothing and finds nothing (a static bookmark list nobody updates) or costs
everything (an agent that re-reads the whole internet every run and burns your budget
re-discovering things it already told you about last week).

## The pattern

Split discovery into cheap generation and expensive evaluation, and never re-evaluate
the same thing twice.

- **Rotating lanes, not one big search.** Instead of one broad "find anything
  interesting" prompt, run several narrow lanes (different sources, different angles
  on the same space) on a rotation. Each lane run is cheap and specific; breadth comes
  from rotating lanes over time, not from making any single run exhaustive.
- **A persistent digest is the memory.** Every candidate the scout has ever surfaced
  goes into a running digest, keyed so a new candidate can be checked against it
  cheaply. A lane run's first job is generating candidates; its second is dropping
  anything already in the digest before spending anything else on it.
- **Score cheap, evaluate expensive, only on the survivors.** Run a fast, cheap fit
  check across everything the lane surfaced. Only the candidates that clear the bar get
  the expensive treatment: a real read, a deep evaluation, a written report. A hard cap
  on how many candidates get the expensive treatment per run keeps cost bounded no
  matter how noisy a lane gets.
- **Additive-only output.** Each run appends a dated report for anything it deep-
  evaluated and adds every candidate it saw to the digest, evaluated or not. Nothing
  gets removed or silently overwritten; the digest only grows, so a later run's dedupe
  check stays honest about what's already been seen.
- **Read-only by default.** The scout finds and reports. Acting on what it finds
  (adopting a tool, reaching out, changing a roadmap) is a separate, human-reviewed
  step, not something the scout does on its own recognizance.

## When to use it

Worth standing up once you're tracking a space that changes often enough that a
one-time survey goes stale in weeks, and you'd rather get a trickle of dated reports
than do an occasional binge search from scratch. Below that, a manual search when you
think of it is cheaper than building the machinery.

## What it isn't

Not a recommendation engine and not a decision-maker. The scout's job ends at "here's
what's new and here's why it might matter." Whether to act on any of it stays a human
call, made with the report in hand, not delegated to the next run.
