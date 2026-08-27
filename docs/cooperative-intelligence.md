# Cooperative intelligence is the larger Breadcrumbs problem

**Status:** pattern essay and research agenda. No new runtime ships in this file.

Breadcrumbs began with a practical question: how can an agent session enter a repository
without rediscovering its rules, current work, and prior corrections? The larger question
is how people, AI systems, and the artifacts between them can cooperate well over time.

That is the direction of Breadcrumbs. It is not a centralized memory product, a claim to
replace human judgment, or a declaration that one architecture solves collaboration. It
is a public pattern kit for building systems where people and agents can orient, hand off,
check one another, learn, and improve without losing custody of the source record.

## The distinction that keeps the work honest

Jarvis is an implementation context. It coordinates bounded work in its owning system.
Breadcrumbs is the public pattern layer. It explains and packages the mechanisms that
prove useful so another team can inspect, adapt, or reject them in its own environment.

That separation matters. A private system can contain personal, institutional, or
operational context. Breadcrumbs never receives that material. It can receive only a
generalized pattern with an evidence link, explicit assumptions, and a clear statement
of whether the mechanism actually ships in this kit.

## The working model

Cooperative intelligence is the quality of the relationship among people, AI systems,
and the tools and records they use together. Breadcrumbs treats it as six connected
concerns:

1. **Orientation.** A new participant can find the current authority, open work, and
   relevant constraints without starting from a transcript dump.
2. **Coordination.** Work has a stated owner, scope, handoff condition, and way to
   detect a collision or stale premise.
3. **Calibrated reliance.** A person can see what supports a result, what remains
   uncertain, and how to correct it. Blind acceptance and reflexive rejection are both
   failures.
4. **Governance.** Authorization, accountability, and review are explicit. A useful
   capability does not create its own permission to act.
5. **Learning.** Evidence, outcomes, corrections, and counterexamples improve the next
   attempt without silently rewriting the record of the last one.
6. **Resilience.** The system notices changed context, degraded connectors, and failed
   handoffs, then degrades safely instead of presenting stale confidence.

The airport model remains the practical picture. A participant should receive the sign
needed at the decision point, not the entire airport manual. The system does the hard
work of preserving boundaries and route truth underneath that simple surface.

## Research is an input, not an automatic feature request

Breadcrumbs uses research to challenge and improve patterns, not to decorate them with
citations. The starting shelf includes organizational accounts of human-AI collaboration
and decision making, such as [Wilson and Daugherty](https://hbr.org/2018/07/collaborative-intelligence-humans-and-ai-are-joining-forces)
and [Jarrahi](https://doi.org/10.1016/j.bushor.2018.03.007). It also includes the
automation-augmentation tension described by [Raisch and Krakowski](https://doi.org/10.5465/amr.2018.0072),
interaction guidance from [Amershi et al.](https://doi.org/10.1145/3290605.3300233),
and research on misuse and disuse of automation from [Parasuraman and Riley](https://doi.org/10.1518/001872097778543886).

Those sources do not certify this kit. They supply questions that an implementation has
to answer with its own evidence.

For each source or field finding, keep three separate outputs:

| Output | What it records | What it must not become |
| --- | --- | --- |
| Evidence | Source, scope, boundary, and confidence | A vague claim that the source proves the system works |
| Method | A reusable review, measurement, or falsification practice | A mandatory process with no stated cost or purpose |
| Architecture impact | Adopt, prototype, watch, defer, or reject, plus a validation plan | An automatic code change |

## The promotion rule

A research idea may become a public Breadcrumbs pattern only when all of the following
are true:

1. Its sources and limits are recorded at the point of claim.
2. At least two independent supports exist, including a cross-disciplinary check when
   the claim crosses fields.
3. A null case is named. The pattern says what result or counterevidence would weaken it.
4. The mechanism has been tested in its owning environment, or is plainly labeled
   pattern-only.
5. The public artifact contains no private source material, internal path, credential,
   or operational state.

This rule makes correction a normal outcome. A rejected pattern, an unknown result, and
a negative evaluation are useful evidence. They are not failures to be hidden.

## Where this goes next

The next phase is not a giant catalog. It is a small, inspectable research cycle:

1. Add a verified source or a bounded field observation.
2. Map it to one of the six concerns and name the boundary condition.
3. Check whether an existing Breadcrumbs artifact already answers it.
4. If not, design one contained experiment in an owning system.
5. Publish a generalized pattern only when the result is inspectable and safe to share.

That keeps Breadcrumbs cumulative without turning it into a private archive or a stack
of claims that no one can test.

For a bounded, pattern-only way to test the work itself, use
[cooperative intelligence evaluation](cooperative-intelligence-evaluation.md). It keeps
orientation, handoff, correction, ownership, and recovery distinct from throughput or
output quality.
