# Collaborative intelligence research method v2.0

**Status:** public research method. It does not implement a runtime, certify a
source as correct, or authorize an architecture change.

Method v2.0 changes the unit of synthesis from a paper to a bounded claim. A
source can support one claim, limit another, and remain irrelevant to a third.
Source count is coverage information, not confidence.

## The three linked records

1. The [source ledger](collaborative-intelligence-research-ledger.md) preserves
   source identity, the first-pass finding, its boundary, and review history.
2. The [source appraisal register](collaborative-intelligence-source-appraisals.md)
   records design, publication state, directness, possible evidence-family
   dependence, time horizon, transfer risk, and linked claim IDs.
3. The [claim register](collaborative-intelligence-claim-register.md) records the
   exact proposition, supporting and contrary evidence, confidence profile,
   null case, and next validation step.

These are research artifacts, not a memory store. Private operational evidence
remains in its owning repository. Breadcrumbs receives only public sources,
public-safe pointers, and permitted aggregate findings.

## Source appraisal

Each source record uses these fields.

| Field | Meaning | Boundary |
|---|---|---|
| Identity | Stable source ID and canonical public pointer | Identity verification does not verify the claim |
| Publication state | Journal, conference, chapter, preprint, working paper, or practitioner report | Publication venue is not a quality score |
| Design | Meta-analysis, review, field experiment, laboratory or online experiment, observational study, survey, benchmark, formal analysis, or conceptual framework | Design type does not establish execution quality |
| Directness | Distance between the study and the target workflow | Directness is not internal validity |
| Evidence family | Possible shared author, dataset, benchmark, laboratory, or research-program lineage | A shared family is a dependence warning, not proof of invalidity |
| Horizon | Single task, repeated interaction, longitudinal use, technical benchmark, or not observed | A long context is not longitudinal evidence |
| Risk and transfer flags | Visible limits from the reviewed record | Screening flags are not a full risk-of-bias assessment |
| Claim links | Claims the source supports, limits, or contradicts | Links do not imply equal evidentiary weight |
| Appraisal depth | Identity-only, screened, full-text appraised, or independently replicated | A source cannot be promoted beyond the recorded depth |

### Directness codes

- `D3 target-like`: current human-AI, agent, or governed-memory work closely
  resembles the bounded workflow under evaluation.
- `D2 adjacent`: directly tests a relevant mechanism, but the task, stakes,
  population, or environment differs materially.
- `D1 analog`: human-team, classical automation, or technical evidence informs
  the question by analogy.
- `D0 conceptual`: theory, taxonomy, or design guidance without a direct test of
  the target claim.

Directness may change by claim. The register records the highest defensible
directness for the linked claims and names transfer limits.

### Appraisal depth

- `identity-only`: canonical source identity was checked.
- `screened`: source page, abstract, and available methods or result summary
  were reviewed far enough to classify design, scope, and visible limits.
- `full-text`: methods, sample, comparator, outcomes, analysis, and limitations
  were appraised against the exact linked claim.
- `replicated`: an independent study or owning-system replay tested the same
  claim under a relevant condition.

The 001 through 100 backfill is `screened`. It is not silently upgraded to a
full-text risk-of-bias review.

## Claim register

Every method-shaping proposition receives a stable `CI-###` identifier and:

- an exact, falsifiable statement;
- applicable workflow conditions;
- supporting, contrary, and limiting source IDs;
- evidence-family count and known dependence;
- a confidence profile;
- a null case or disconfirmation trigger;
- a controlled disposition; and
- the next owning-system test or research need.

One source may appear in several claims. One claim may remain contested even
with many supporting papers when those papers share a narrow evidence family.

## Confidence is a profile

Method v2.0 does not calculate one confidence score. Each claim reports six
dimensions separately.

| Dimension | Values | Question |
|---|---|---|
| Directness | high, moderate, low | Does the evidence test the target workflow? |
| Validity | high, moderate, low, not fully appraised | How credible is the reviewed design for this exact claim? |
| Independence | high, moderate, low, unknown | Do separate evidence families support the claim? |
| Consistency | convergent, mixed, contested, sparse | Do results agree after context is considered? |
| Transfer | narrow, bounded, broad, unknown | How far may the finding travel beyond the studied setting? |
| Durability | longitudinal, repeated, single-task, technical-only, unknown | Does the evidence survive time or change? |

A profile can be method-shaping even when one dimension is weak. The weak
dimension remains visible and becomes a research or evaluation requirement.

## Controlled dispositions

Use one disposition at claim level.

- `adopt-method`: change the research or evaluation method now.
- `prototype`: run a bounded owning-system test without claiming deployment
  validity.
- `watch`: retain the claim and seek specified evidence.
- `defer`: take no architecture action until a named condition is satisfied.
- `reject-generalization`: reject the broad claim while allowing narrower,
  testable variants.
- `no-change`: the evidence does not alter the current method or architecture.

`Strengthen` is retired as a disposition because it did not state what changed.
Earlier source rows preserve it as historical v1 language.

## Corroboration and contradiction

Two source IDs do not automatically create corroboration. A claim is:

- `emerging` when one evidence family supplies direct support;
- `corroborated` when at least two meaningfully independent evidence families
  support the same bounded claim;
- `contested` when relevant contrary evidence changes the expected result or
  boundary; or
- `unresolved` when screening cannot distinguish dependence, validity, or
  transfer.

Record contradictions at claim level. Do not resolve them by majority count.
First test whether population, task structure, expertise, stakes, comparator,
time horizon, or model version explains the difference.

## Research collection log

Every future wave records:

- research question and target claim IDs;
- search date, sources searched, and query strings;
- inclusion and exclusion rules;
- duplicate and evidence-family checks;
- screening count and exclusion reasons;
- date boundary and known inaccessible material; and
- whether the wave is systematic, purposive, or gap-directed.

The first 100 sources form a purposive evidence map. They are not a systematic
review and must not be described as exhaustive.

## Change and expiry

Recheck a source or claim when any of these changes materially:

- publication state or correction status;
- model, prompt, tool, policy, or data distribution;
- participant expertise or decision authority;
- target task, stakes, reversibility, or feedback latency;
- benchmark, dataset, judge, or outcome definition; or
- the owning system's implementation.

A moved source triggers identity re-verification. It does not by itself make the
underlying finding false. A superseded claim remains visible with its replacement
and reason.

## Promotion rule

A claim may shape the public method when its confidence profile and limits are
explicit. A claim may become a reusable implementation pattern only when:

1. at least two meaningfully independent evidence families support it;
2. contrary evidence and the null case are recorded;
3. a relevant owning-system test has inspectable evidence;
4. change and expiry conditions are named; and
5. the public artifact contains no private source record or unapproved detail.

No literature result grants runtime authority, publication approval, or access
to a new data source.
