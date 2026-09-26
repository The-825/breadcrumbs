# Cooperative intelligence is the larger Breadcrumbs problem

**Status:** pattern essay and research agenda. No new runtime ships in this file.

Breadcrumbs began with a practical question: how can an agent session enter a repository
without rediscovering its rules, current work, and prior corrections? The larger question
is how people, AI systems, and the artifacts between them can cooperate well over time.

In this paper, **collaborative intelligence** names the quality of a bounded human-AI or
multi-agent interaction: whether participants can divide work, calibrate reliance,
preserve judgment, correct one another, and produce a better outcome than the strongest
relevant alternative. **Cooperative intelligence** is the wider systems problem:
whether those interactions remain governable, inspectable, resilient, and cumulative
across people, agents, tools, records, and time.

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
and the tools and records they use together. The current evidence base supports six
connected concerns:

1. **Orientation.** A new participant can find the current authority, open work, and
   relevant constraints without starting from a transcript dump.
2. **Coordination.** Work has a stated owner, scope, dependency structure, handoff
   condition, and way to detect a collision or stale premise.
3. **Calibrated reliance.** A person can see what supports a result, what remains
   uncertain, and how to correct it. Blind acceptance and reflexive rejection are both
   failures. Reliance is evaluated behaviorally: correct acceptance, incorrect
   acceptance, justified resistance, unjustified resistance, verification, escalation,
   and recovery are distinct outcomes.
4. **Governance.** Authorization, accountability, and review are explicit. Information
   acquisition, analysis, recommendation, decision, and action can require different
   authority. A useful capability does not create its own permission to act.
5. **Learning.** Evidence, outcomes, corrections, and counterexamples improve the next
   attempt without silently rewriting the record of the last one. Same-model critique or
   self-refinement can improve an artifact but does not count as independent verification
   of a durable claim, correction, or authority change.
6. **Resilience.** The system notices changed context, degraded connectors, model or tool
   changes, failed handoffs, and stale premises, then revalidates or degrades safely
   instead of presenting stale confidence.

The airport model remains the practical picture. A participant should receive the sign
needed at the decision point, not the entire airport manual. The system does the hard
work of preserving boundaries and route truth underneath that simple surface.

## What the framework now measures separately

The research record has made several collapsed ideas unusable. Breadcrumbs therefore
keeps the following distinctions explicit.

### Outcome quality is not collaboration quality

A joint system is not better merely because it produces a strong final artifact.
Generation, selection, review, correction, handoff, action, and closeout can have
different owners and failure modes. Collaboration benefit is conditional: compare the
joint system with the strongest relevant individual or established-workflow baseline,
not only with a weak or unsupported alternative.

### Capability is not authority

Capability is task-, context-, tool-, participant-, and version-specific. A system may
be competent to retrieve information without being authorized to recommend, decide, or
act. Authority is bound to function and consequence, not granted once at the agent level.

### Trust is not appropriate reliance

Stated trust, confidence, explanation presence, preference, agreement, and adoption are
not substitutes for behavior. The framework asks whether participants accept good help,
reject bad help, verify when warranted, escalate when needed, and recover after error.

### Explanation is not verification

An explanation must have a named behavioral purpose: error detection, correction,
escalation, appropriate reliance, or another observable target. A fluent rationale can
increase confidence without improving correction. Self-explanation and same-family
critique remain refinement signals, not independent evidence.

### Memory is not recall

Useful memory includes retrieval, updates, abstention, temporal and causal reasoning,
role, efficiency, capacity, provenance, correction, custody, isolation, and deletion.
A remembered statement is not automatically current, authorized, or true.

### More agents are not automatically more intelligence

Additional agents are justified only when decomposition, topology, specialized
capability, or genuinely independent information improves a bounded outcome enough to
justify the added cost and coordination burden. Agent count is not a quality metric.

## A longitudinal interaction model

The current framework treats collaborative intelligence as a property of a governed
trajectory, not a single response.

A useful abstraction is:

**task and state → role allocation → evidence gathering → recommendation or action →
human/agent review → reliance or resistance → outcome → correction → revalidation →
updated shared state**

Each transition can be inspected separately.

For consequential work, the practical questions become:

- What capability is being exercised at this step?
- Who or what owns the step?
- What evidence supports it?
- What uncertainty or applicability limit remains?
- What authority permits the next transition?
- What would cause escalation, abstention, or rollback?
- What trace is needed to diagnose failure without retaining unnecessary private data?
- What material change would invalidate the evidence that justified this routing rule?

This is a working architecture hypothesis assembled from the active claim set. It is not
a claim that one fixed workflow fits every domain.

## Current evidence-backed operating rules

The [claim register](collaborative-intelligence-claim-register.md) currently supports the
following method-level rules:

1. **Use the strongest relevant baseline.** Human-AI or multi-agent collaboration earns a
   benefit claim only when it improves the bounded outcome against the best relevant
   alternative, including cost, burden, safety, and quality where they matter.
2. **Evaluate the trajectory.** Final-output quality cannot substitute for evidence about
   orientation, handoff, verification, correction, ownership, recovery, and closeout.
3. **Calibrate reliance behaviorally.** Track acceptance, override, verification,
   escalation, and recovery after both correct and incorrect assistance.
4. **Bind authority to function and consequence.** Retrieval, analysis, recommendation,
   decision, and action can receive different permissions.
5. **Expire evidence after material change.** Model, prompt, tool, policy, data,
   participant, and task changes can invalidate earlier delegation or trust evidence.
6. **Preserve meaningful human authority.** Review or takeover rights are not meaningful
   if mode, routing, or system state is hidden or if the person cannot recover after
   routine automation.
7. **Keep explanation goal-specific.** Evaluate explanations by the behavior they are
   intended to improve and record side effects such as bias, burden, or unjustified
   confidence.
8. **Do not confuse self-refinement with independent verification.** Durable changes need
   evidence from an independent source, tool, evaluator, or human-owned decision when the
   consequence warrants it.
9. **Treat memory as governed state.** Retrieval quality is only one property; source
   precedence, correction survival, custody, isolation, deletion, and stale-context
   rejection remain separate requirements.
10. **Make multi-agent complexity earn its keep.** Compare against one strong agent or
    established workflow under matched budgets and unseen work before widening the
    architecture.

These rules are method-shaping. They do not certify a runtime implementation.

## September 2026 research-watch extension

The ongoing research watch has surfaced several additional ideas that are relevant enough
to shape experiments and writing, but have **not yet been promoted into the public claim
register through the full source-appraisal process**. They remain provisional until that
review is complete.

### Relational alignment is not epistemic warrant

Recent human-subject work suggests that agreement, value congruence, familiarity, and
feeling understood can increase willingness to accept AI advice. The working hypothesis
is that collaboration should distinguish **relational alignment** from **epistemic
warrant**. A system can fit the person well without thereby earning stronger evidentiary
status for its claims.

**Status:** interpretation supported by emerging experiments; not yet a promoted
Breadcrumbs claim.

### Reliability should be case-conditioned

Recent clinical and decision-support work suggests that behavioral stability,
applicability, evidence quality, consequence severity, and verification availability can
all matter when deciding whether to act, ask, escalate, or abstain. Stability can be
useful without being independent corroboration: a model that agrees with itself several
times can still be consistently wrong.

**Status:** emerging design direction; thresholds and transfer conditions are not
established.

### Unknown and ambiguity should be actionable states

Open-set recognition and human-robot dialogue work suggest that a system should be able
to represent that the current case falls outside its known categories or contains a
specific ambiguity, rather than forcing every state into the nearest known answer.

A candidate interaction sequence is:

**uncertain → classify ambiguity or non-applicability → ask / confirm / observe / refuse /
escalate / act under constraint**

**Status:** promising cross-domain hypothesis; live human-AI validation remains limited.

### Role structure matters more than agent count

Recent multi-agent studies increasingly separate role diversity, capability diversity,
model diversity, and evidence diversity. Structured specialization, critique, and
reconciliation can improve selected tasks, while generic critic agents or additional
agents can add cost or reduce quality.

**Status:** technically supported in bounded benchmarks and selected domain studies;
human-AI transfer remains an open question.

### Verification capacity may constrain safe complementarity

A recurring pattern is that people can benefit from AI most where they lack knowledge,
while that same gap can reduce their ability to independently validate the help. The
working hypothesis is to represent **need for assistance** and **capacity to verify** as
different variables. High need plus low verification capacity may justify stronger
grounding, independent review, or escalation rather than greater autonomy.

**Status:** interpretation of emerging human-subject evidence; not yet a promoted claim.

### Shared state is a governed commons

Recent multi-agent work shows that shared artifacts can coordinate participants who never
directly interact, but can also amplify bad conventions, exploits, or correlated
assumptions. Provenance supports detection, but governance may also require challenge,
quarantine, supersession, retraction, and propagation control.

**Status:** strong architecture hypothesis from agent-system evidence; human-team evidence
is still limited.

### Evaluation evidence needs its own provenance

Simulation, synthetic users, virtual environments, automated judges, and LLM-based human
proxies do not carry the same evidentiary weight as real-world human behavior. A useful
evaluation record should therefore state the environment, comparator, evaluator, proxy
role, uncertainty, transfer boundary, and failure modes a metric can conceal.

**Status:** methodological refinement supported by recent reviews and benchmark work;
specific minimum standards remain open.

These provisional refinements should be promoted only after the
[research method](collaborative-intelligence-method-v2.md) links them to bounded source
families, contrary evidence, null cases, and explicit transfer limits.

## Research is an input, not an automatic feature request

Breadcrumbs uses research to challenge and improve patterns, not to decorate them with
citations. The starting shelf includes organizational accounts of human-AI collaboration
and decision making, such as [Wilson and Daugherty](https://hbr.org/2018/07/collaborative-intelligence-humans-and-ai-are-joining-forces)
and [Jarrahi](https://doi.org/10.1016/j.bushor.2018.03.007). It also includes the
automation-augmentation tension described by [Raisch and Krakowski](https://doi.org/10.5465/amr.2018.0072),
interaction guidance from [Amershi et al.](https://doi.org/10.1145/3290605.3300233),
and research on misuse and disuse of automation from
[Parasuraman and Riley](https://doi.org/10.1518/001872097778543886).

Those sources do not certify this kit. They supply questions that an implementation has
to answer with its own evidence.

For each source or field finding, keep three separate outputs:

| Output | What it records | What it must not become |
| --- | --- | --- |
| Evidence | Source, scope, boundary, and confidence | A vague claim that the source proves the system works |
| Method | A reusable review, measurement, or falsification practice | A mandatory process with no stated cost or purpose |
| Claim disposition | Adopt-method, prototype, watch, defer, reject-generalization, or no-change, plus a validation plan | An automatic code change |

The source itself is not the unit of promotion. Use
[research method v2.0](collaborative-intelligence-method-v2.md) to appraise the
source, then update the bounded proposition in the
[claim register](collaborative-intelligence-claim-register.md). This prevents
multiple papers from one evidence family from becoming independent votes.

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

1. Name the target claim or gap before searching.
2. Record the search path, exclusions, and possible evidence-family dependence.
3. Add a verified source or a bounded field observation to the source register.
4. Link it to the exact claim it supports, limits, or contradicts.
5. Check whether an existing Breadcrumbs artifact already answers it.
6. If not, design one contained experiment in an owning system.
7. Publish a generalized pattern only when the result is inspectable and safe to share.

The immediate research-watch priority is to take the provisional September refinements
above through the claim method one by one. The most important questions are:

- When does relational alignment improve collaboration, and when does it merely increase
  persuasion or acceptance?
- Which case-level signals justify act / ask / escalate / abstain decisions without
  turning self-consistency into false corroboration?
- Which ambiguity classes produce safer or lower-burden interaction policies than a
  generic confidence threshold?
- Which role topologies improve outcomes under equal cost, and which simply create more
  coordination overhead?
- How should verification capacity be measured without inferring broad competence from a
  narrow task?
- What governance operations are necessary for shared memory to remain correctable under
  contamination, drift, or disagreement?
- What proxy-validity and ecological-transfer evidence is required before simulation
  results may support claims about real human-AI teams?

That keeps Breadcrumbs cumulative without turning it into a private archive or a stack
of claims that no one can test.

For a bounded, pattern-only way to test the work itself, use
[cooperative intelligence evaluation](cooperative-intelligence-evaluation.md). It keeps
orientation, handoff, correction, ownership, and recovery distinct from throughput or
output quality.
