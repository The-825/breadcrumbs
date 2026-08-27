# Evaluate cooperative intelligence without inventing a score

**Status:** public, pattern-only evaluation method. No evaluator or runtime capability
ships in this document.

The failure this method prevents is calling a system "collaborative" because one person
worked faster with a model. That measures individual assistance, not cooperation.

Use this method when people, AI systems, and durable artifacts share a bounded work
item. It keeps individual throughput, coordination, and recovery separate, so a gain in
one cannot hide failure in another.

## What one evaluation covers

One evaluation covers a bounded work item from orientation through closeout. The work
item must name its owner, intended outcome, authority boundary, source record, and
handoff condition before anyone starts. It may be a task, review, incident, or research
cycle. It is not an entire organization or a model's general capability.

Record the participating roles, tool versions, and available evidence. Do not put raw
private content, credentials, student information, customer material, or internal paths
in a public record. Keep those source records in their owning system and retain only
safe pointers or aggregate results where disclosure is permitted.

Before comparing conditions, profile the work item. Record stakes, consequence,
reversibility, feedback latency, participant expertise, task decomposability,
privacy and authority constraints, expected duration, and the model, prompt,
tool, policy, and data versions that bound the result. These fields determine
which evidence transfers and when a prior evaluation expires.

## Compare the right conditions

Compare only conditions that answer the same task question. When feasible, record:

1. human-only work;
2. AI-only work, when a safe and authorized version exists;
3. cooperative work, with the stated human and AI roles; and
4. the previous established workflow, if it differs from human-only work.

No fixed sample count makes a result reliable. State what was compared, what could not
be compared, and why. A cooperative result does not count as a gain merely because it
beats the weakest baseline. Report whether it beats the best available baseline or
remains unknown.

This follows the best-baseline concern in the [research ledger](collaborative-intelligence-research-ledger.md), including the meta-analysis by [Vaccaro, Almaatouq, and Malone](https://doi.org/10.1038/s41562-024-02024-1). It is a measurement rule, not a claim that every task can or should run every comparison.

## Evaluate five separate concerns

| Concern | Question | Acceptable evidence | Failure signal |
|---|---|---|---|
| Orientation | Could a new, authorized participant find current authority, constraints, and source pointers without a transcript dump? | Reproducible clean-start result with cited artifacts | Participant starts from stale or uncited context |
| Handoff | Did the next participant receive owner, scope, expected outcome, limits, and a completion condition? | Bounded handoff record and recipient verification | Work is duplicated, blocked, or completed against the wrong premise |
| Correction | Did an accepted correction reach the artifact or rule that caused the error, and survive regeneration or session change? | Dated correction record plus a repeat or replay check | The same corrected error returns |
| Ownership | Did each participant stay within its stated authority, especially at consequential boundaries? | Authority record, action log, and review evidence | An actor widened scope, acted without approval, or could not show who owned the decision |
| Recovery | Did the system detect changed context, failed evidence, or a degraded connector and return a safe, current state? | Stale-context or failure drill with its observed result | Stale output is presented as current or the system silently guesses |

Keep individual output quality, time, cost, and user burden as additional outcome fields.
They can matter, but none substitutes for the five concerns. A six-month field experiment
found changes to independently controlled work without a significant change to a
coordination-dependent measure, which is why throughput and coordination remain
separate here. See [Dillon et al.](https://www.microsoft.com/en-us/research/publication/shifting-work-patterns-with-generative-ai/).

## Activate only relevant modules

The five concerns remain the core governance and continuity checks. Add a module
only when the work item exposes its risk. Do not turn every evaluation into one
large checklist.

| Module | Activate when | Required observation | Failure signal |
|---|---|---|---|
| Grounding | Participants must coordinate across a handoff or repository boundary | Shared objective, constraints, owner, correction state, and recipient acknowledgement | Work proceeds from a wrong premise or requires unbounded source copying |
| Reliance and deferral | A person or agent may accept, reject, override, or route advice | Acceptance, verification, override, escalation, abstention, and outcome | Confidence or role label substitutes for calibrated behavior |
| Explanation behavior | An explanation is intended to change a decision behavior | Predeclared behavior, observed effect, burden, and side effects | Confidence rises without better detection, correction, or escalation |
| Mode and reentry | Automation changes mode, routing, or active control | Visible state plus safe takeover or stale-context drill | The participant cannot identify the mode or recover safely |
| Skill retention | Work repeats or may remove practice from a responsible person | Independent performance or recovery after repeated assistance | Routine gains coexist with lost intervention ability |
| Portfolio diversity | The work generates repeated research, writing, or design options | Quality and diversity across the complete portfolio | Average quality rises while useful option diversity collapses |
| Fairness and accessibility | Outcomes may differ across groups, abilities, languages, or access modes | Disaggregated outcomes and participation burden | Aggregate benefit hides subgroup harm or exclusion |
| Retrieval and memory governance | Prior records or retrieved evidence affect the result | Query fit, leaf provenance, version, correction, tombstone, isolation, and deletion behavior | Recall succeeds while stale, unauthorized, or corrected evidence remains active |
| Adversarial safety | Tools or retrieved content can contain untrusted instructions | Utility and attack outcome under the same authority boundary | The system follows untrusted content or widens authority |

## Run the protocol

1. Define the work item, workflow profile, and authority boundary before exposing it to a participant.
2. Select a matched baseline or record why no safe baseline exists.
3. Select only the conditional modules required by the workflow profile.
4. Run the work through the stated roles without changing the target outcome midway.
5. Record each concern and selected module as observed, failed, or unknown. Unknown is not a failure and is
   not a pass.
6. Attempt one safe recovery or correction check when the work exposes a relevant
   premise, handoff, or source. Do not manufacture a harmful failure in production.
7. Compare outcomes by task stage. Generation, selection, review, correction, and
   closeout may have different owners and different results.
8. Record the change manifest that would expire the result.
9. Publish or retain only the level of detail permitted by the owning environment.
   A public pattern can name the method and aggregate outcome. It must not reveal the
   underlying private work item.

The stage distinction matters because a workplace field experiment found that AI-assisted
idea generation and human evaluative selection can differ. See [Dell'Acqua et al.](https://doi.org/10.1287/orsc.2025.20702). That result is a reason to separate stages, not a universal role-allocation rule.

## Make a bounded conclusion

Use one of these conclusions for each concern:

- **supported in this evaluation:** the stated evidence was observed for the defined
  work item and condition;
- **failed in this evaluation:** the stated failure signal was observed;
- **unknown:** evidence is absent, incomplete, or not safely comparable; or
- **not evaluated:** the concern did not apply to the bounded work item.

Do not collapse the five concerns into one collaboration number. An aggregate score can
hide a safety or correction failure behind better throughput. If a team later needs a
summary, publish coverage first: which concerns have evidence, which are unknown, and
which failed.

Report conditional modules the same way. A module is not a new score component.
Its result stays separate so a productivity gain cannot offset a reliance,
fairness, memory, or adversarial-safety failure.

## What this method does not establish

This method does not prove general intelligence, organizational transformation, durable
trust, or superiority of multi-agent work. It does not grant authority, replace an
owning system's governance, or justify moving source records into Breadcrumbs.

Before generalizing a result, obtain independent support, name the null case, and rerun
the protocol in a different relevant condition. The promotion rule remains in
[cooperative intelligence](cooperative-intelligence.md), and evidence strength
is recorded through [research method v2.0](collaborative-intelligence-method-v2.md).

## Copyable record

Copy [the evaluation template](../templates/COOPERATIVE_INTELLIGENCE_EVALUATION_TEMPLATE.md)
into the owning repository. Keep the completed record there. Only publish a generalized
method or permitted aggregate finding.
