# Collaborative intelligence research ledger

Status: public research method and first-pass synthesis. This document does not
implement a runtime capability, certify novelty, or establish that any cited author
reviewed this repository.

Only public source material and public repository evidence enter this ledger.

## Purpose

This ledger tests the broader collaborative-intelligence framing around Breadcrumbs
without turning each paper into a new architectural principle. It records what a
source supports, what it does not support, and what question should be investigated
next. Architecture changes only after evidence converges across sources or a bounded
implementation test produces a result.

## Method v1.0

Each source carries the same fields:

1. source identity and verification status;
2. level of analysis: task, interaction, workflow, organization, or ecosystem;
3. decision context: structured, semi-structured, or unstructured;
4. evidence type and scope;
5. claims relevant to this repository;
6. architecture impact: adopt, strengthen, watch, reject, or no change;
7. corroborating and contradicting evidence;
8. boundaries and assumptions;
9. the next best research question; and
10. method version.

Metadata enrichment, such as adding a level-of-analysis field, is backfilled across
prior entries. Analytical enrichment, such as changing a finding, requires rereading
the source. A method change never silently becomes an architecture change.

## Source ledger

| ID | Source | Level and evidence | First-pass finding | Architecture impact | Boundary and next question |
|---|---|---|---|---|---|
| 001 | H. James Wilson and Paul R. Daugherty, ["Collaborative Intelligence: Humans and AI Are Joining Forces"](https://hbr.org/2018/07/collaborative-intelligence-humans-and-ai-are-joining-forces), *Harvard Business Review*, 2018 | Organization and workflow; reported study of 1,500 companies plus organizational examples | Human and machine strengths can complement each other, but value depends on redesigning work around collaboration rather than adding AI to an unchanged process. | **Strengthen** complementarity and workflow redesign. No new principle. | This is organizational evidence, not proof of durable cross-session protocols. Next: what makes a redesigned workflow persist after participants or models change? |
| 002 | Andreas Fügener, Dominik D. Walzner, and Alok Gupta, ["Roles of Artificial Intelligence in Collaboration with Humans: Automation, Augmentation, and the Future of Work"](https://doi.org/10.1287/mnsc.2024.05684), *Management Science*, published online 2025, volume 72 in 2026 | Task; analytical allocation model validated with experimental image-classification data | Automation, augmentation, and human-only work are task-allocation choices. Their value depends on between-task and within-task complementarity, task difficulty, and the ability to reallocate human effort. | **Test as a candidate capability:** evidence-based work allocation. Do not convert it into a universal routing rule. | The experiment uses idealized judgment tasks with known ground truth. Next: which non-performance factors, including consequence, accountability, and privacy, must constrain allocation? |
| 003 | Mohammad Hossein Jarrahi, ["Artificial Intelligence and the Future of Work: Human-AI Symbiosis in Organizational Decision Making"](https://doi.org/10.1016/j.bushor.2018.03.007), *Business Horizons* 61(4), 2018 | Decision and organization; conceptual synthesis | AI contributes analytical processing under complexity while humans retain holistic and intuitive strengths under uncertainty and equivocality. | **Strengthen** human judgment under uncertainty. Add decision context to future reviews. No new principle. | Conceptual framing does not measure a deployed collaboration protocol. Next: how should a system recognize when uncertainty calls for human judgment rather than more model effort? |
| 004 | Adiata Borresa Seini, Ibrahim Osman Adam, and Mansah Preko, ["Human-AI Collaboration in Information Systems Research: A Systematic Literature Review and Future Research Directions"](https://doi.org/10.1007/s42454-026-00100-7), *Human-Intelligent Systems Integration*, 2026 | Interaction, organization, and ecosystem; systematic review of 137 articles | The literature converges on redefined human-machine relationships, interaction design, and organizational-societal implications. It still lacks longitudinal evidence, unified evaluation frameworks, and sufficient theoretical grounding. | **Strengthen** the collaborative frame. **Watch** evaluation and longitudinal continuity as research debt, not claimed contributions. | A literature gap does not prove this repository fills it. Next: what evaluation scheme can compare collaboration quality without collapsing unlike contexts into one score? |

### Entry metadata

| ID | Identity verification | Decision context | Corroboration and contradiction | Method |
|---|---|---|---|---|
| 001 | Verified 2026-08-26 against the public HBR article page | Semi-structured organizational work | Corroborated by 002, 003, and 004 on complementarity; no negative-evidence source reviewed yet | v1.0 |
| 002 | Verified 2026-08-26 against the INFORMS publication page and DOI metadata | Structured judgment tasks with known ground truth | Corroborates complementarity and task allocation; scope limits transfer to open-ended or consequential work | v1.0 |
| 003 | Verified 2026-08-26 against DOI metadata and the publicly available abstract | Semi-structured and unstructured organizational decisions | Corroborated by 002 on difficult-task human contribution and by 004 on human-centered collaboration; conceptual rather than deployed evidence | v1.0 |
| 004 | Verified 2026-08-26 against the Springer article page and DOI metadata | Cross-context literature synthesis | Corroborates the overall frame and records longitudinal, evaluation, and theory gaps; no negative-evidence source reviewed yet | v1.0 |

## Corroboration matrix

Status meanings: **emerging** has one direct source, **corroborated** has support from
at least two independently scoped sources, and **contested** has material contrary
evidence. Absence of contradiction is not confirmation.

| Candidate pattern | 001 | 002 | 003 | 004 | Current status | Repository consequence |
|---|---|---|---|---|---|---|
| Human-AI complementarity | supports | supports | supports | synthesizes | corroborated | Keep collaboration, not replacement, as the frame. |
| Workflow redesign | supports | task-level implication | neutral | synthesizes | corroborated | Evaluate the surrounding workflow, not only the model response. |
| Evidence-based work allocation | neutral | direct support | compatible | compatible | emerging | Treat allocation as a candidate capability and test it against consequential work. |
| Human judgment under uncertainty | compatible | supports human-only handling for difficult tasks | direct support | compatible | corroborated | Preserve explicit human-owned judgments and escalation criteria. |
| Interaction quality as an outcome | compatible | partially measurable through performance | compatible | direct synthesis | corroborated but underspecified | Define measures before claiming improvement. |
| Longitudinal continuity | not tested | not tested | not tested | names a literature gap | emerging research debt | Breadcrumbs may provide a test bed, but current implementation is not research validation. |
| Unified collaboration evaluation | not supplied | task-performance measure only | not supplied | names a literature gap | emerging research debt | Do not publish one composite score as settled science. |
| Multi-AI coordination | not tested | not tested | not tested | adjacent, not resolved | unresolved | Keep as an open question, not a supported contribution. |

No contested pattern has been identified in this four-source pass. That means the next
search should deliberately seek negative evidence rather than adding another friendly
source.

## Dependency map

This is a working architecture hypothesis, not a finding attributed to the four papers.

1. **Principles** state what should remain true, including traceable evidence and
   preserved human authority.
2. **Capabilities** state what the system must be able to do, including continuity,
   coordination, evidence tracing, trust calibration, recoverability, governance,
   learning, and candidate work allocation.
3. **Patterns** describe repeatable ways to realize capabilities.
4. **Protocols** coordinate participants and make handoffs inspectable.
5. **Implementations** bind the protocols to current tools, models, and repositories.

Evidence may strengthen or weaken any layer. A new implementation does not establish a
new principle, and a literature gap does not certify an implementation as the answer.

## Ranked research questions

1. How should collaboration quality be evaluated across task, workflow, and
   organizational levels without creating a misleading composite score?
2. Which protocols preserve coordination and correction over time as people, models,
   and tools change?
3. How should consequence, privacy, accountability, and uncertainty constrain
   evidence-based work allocation?
4. What evidence would distinguish multi-AI coordination from several independent
   agents sharing a queue?
5. Which findings survive outside idealized tasks with known ground truth?

## Method change log

| Version | Change | Evidence or reason | Prior entries affected |
|---|---|---|---|
| 1.0, 2026-08-26 | Established the common source fields, architecture-impact labels, corroboration states, negative-evidence requirement, dependency map, and ranked-question queue. | Four-source checkpoint review exposed repeated drift between paper summaries and architecture claims. | 001 through 004 received the same metadata backfill. |

## Research debt

- Seek at least one source that reports failed or harmful human-AI collaboration.
- Define an evaluation unit before adding a collaboration score.
- Test whether the candidate work-allocation capability survives consequential,
  privacy-constrained, and open-ended work.
- Keep source identity verification separate from claim verification.
- Revisit every earlier entry when a major method version changes. Minor metadata
  additions may be backfilled without changing the finding.
