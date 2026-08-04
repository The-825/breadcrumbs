# ADR template for data platforms

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

A year from now, someone will ask why the warehouse is laid out this way, and the answer will live in nobody's head. Architecture decision records are the cheap fix: one page per decision, written when the decision is made, filed in `docs/adr/` and never deleted. On a data platform the decisions most worth recording are the quiet ones: dataset layout, ingestion typing, where flags and config live, what counts as the canonical store. Those are exactly the calls a future rebuild pays to re-discover.

## The format

```markdown
# ADR-<n>: <short title of the decision>

Date: <YYYY-MM-DD>
Status: <proposed | accepted | superseded by ADR-<n>>

## Context

<What forced a decision. The constraint, the failure, or the fork in the road.
Two to five sentences.>

## Decision

<The call, stated plainly. "We will..." One paragraph.>

## Consequences

<What gets easier, what gets harder, what we are now committed to. Include the
costs; an ADR with no downsides recorded was not thought through.>

## Alternatives considered

<Each rejected option in a line or two, with the reason it lost. This section
is what stops the debate from being reopened cold.>
```

## Filled example

```markdown
# ADR-3: Layered warehouse datasets instead of one shared dataset

Date: 2026-02-09
Status: accepted

## Context

All tables currently live in one shared dataset. Analysts query raw ingestion
tables directly, so every upstream schema change breaks dashboards, and there
is no place to put cleaned or derived data that is obviously distinct from raw.

## Decision

We will split the warehouse into three layers: `raw_` datasets that ingestion
writes and nothing else reads directly, a `staging` dataset of typed and
deduplicated tables, and a `marts` dataset of views that dashboards and the
API read. Consumers point at marts only.

## Consequences

Upstream schema drift stops reaching dashboards; it gets absorbed in staging.
Every new source now needs a staging model before anyone can use it, which
adds a step to onboarding a source. Existing dashboards must be repointed to
marts views, a one-time migration we accept.

## Alternatives considered

Keep the single dataset with naming conventions only: rejected, conventions
without boundaries decay, and nothing stops a dashboard from reading raw.
Per-team datasets: rejected, duplicates the same source logic per team and
splits the definition of core metrics.
```

Write the ADR the day the decision lands. A week later the alternatives are already fading, and a year later the record is the only defense the decision has.
