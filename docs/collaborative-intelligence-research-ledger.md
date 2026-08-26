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
| 005 | Gagan Bansal et al., ["Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance"](https://doi.org/10.1145/3411764.3445717), *CHI*, 2021 | Task and interaction; mixed-method user studies across three datasets | AI assistance produced some complementary performance, but explanations did not increase it. Explanations increased acceptance of recommendations whether they were right or wrong. | **Reject** explanation presence as a proxy for collaboration quality. **Strengthen** separate measurement of human-only, AI-only, and team outcomes. | The tasks were bounded classification and reasoning tasks. Next: which outcome set captures quality, effort, reversibility, and accountability in open-ended work? |
| 006 | Gary Klein, David D. Woods, Jeffrey M. Bradshaw, Robert R. Hoffman, and Paul J. Feltovich, ["Ten Challenges for Making Automation a Team Player in Joint Human-Agent Activity"](https://doi.org/10.1109/MIS.2004.74), *IEEE Intelligent Systems* 19(6), 2004 | Interaction and workflow; conceptual challenge framework grounded in joint-activity research | Useful teammates must support coordination, common ground, mutual predictability, and direction rather than behave as isolated tools. | **Strengthen** the protocol layer. **Test** whether handoffs expose enough status, intent, limits, and correction state for another participant to coordinate safely. | A challenge framework is not a validation of this repository's protocol. Next: which challenges can be turned into observable conformance checks across session and model changes? |
| 007 | John D. Lee and Katrina A. See, ["Trust in Automation: Designing for Appropriate Reliance"](https://pubmed.ncbi.nlm.nih.gov/15151155/), *Human Factors* 46(1), 2004 | Interaction and decision; multidisciplinary review and conceptual model | Trust affects reliance when full understanding is impractical, but the design goal is appropriate reliance calibrated to context and automation performance, not maximum trust. | **Strengthen** calibrated reliance and evidence display. **Reject** confidence or user acceptance as sufficient evidence of safe collaboration. | The review predates current generative systems. Next: which observable behaviors show appropriate reliance when outputs and system capability change between runs? |
| 008 | Qingyun Wu et al., ["AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation"](https://www.microsoft.com/en-us/research/publication/autogen-enabling-next-gen-llm-applications-via-multi-agent-conversation-framework/), *COLM*, 2024 | Workflow and implementation; framework description plus pilot applications across several domains | Configurable agents, tools, human input, and conversation patterns can compose multi-agent applications. The paper demonstrates feasibility and flexibility, not a general advantage over one agent or proof of governance. | **Watch** as implementation evidence. Do not promote conversational multiplicity into a coordination principle or performance claim. | Pilot applications do not isolate when extra agents help, duplicate work, or amplify error. Next: what matched evaluation distinguishes coordination benefit from added calls and shared context? |
| 009 | Zana Buçinca, Maja Barbara Malaya, and Krzysztof Z. Gajos, ["To Trust or to Think: Cognitive Forcing Functions Can Reduce Overreliance on AI in AI-Assisted Decision-Making"](https://doi.org/10.1145/3449287), *Proceedings of the ACM on Human-Computer Interaction* 5(CSCW1), 2021 | Task and interaction; experiment with 199 participants | Cognitive-forcing interventions reduced overreliance more than simple explanation interfaces, but the strongest interventions received the least favorable subjective ratings and effects varied with need for cognition. | **Strengthen** deliberate review at consequential boundaries. **Test** proportionate friction rather than adding a universal interruption. | One experimental task does not establish the right intervention for sustained professional work. Next: what is the least disruptive intervention that improves error detection for a given consequence level? |

### Entry metadata

| ID | Identity verification | Decision context | Corroboration and contradiction | Method |
|---|---|---|---|---|
| 001 | Verified 2026-08-26 against the public HBR article page | Semi-structured organizational work | Corroborated by 002, 003, and 004 on complementarity; no negative-evidence source reviewed yet | v1.0 |
| 002 | Verified 2026-08-26 against the INFORMS publication page and DOI metadata | Structured judgment tasks with known ground truth | Corroborates complementarity and task allocation; scope limits transfer to open-ended or consequential work | v1.0 |
| 003 | Verified 2026-08-26 against DOI metadata and the publicly available abstract | Semi-structured and unstructured organizational decisions | Corroborated by 002 on difficult-task human contribution and by 004 on human-centered collaboration; conceptual rather than deployed evidence | v1.0 |
| 004 | Verified 2026-08-26 against the Springer article page and DOI metadata | Cross-context literature synthesis | Corroborates the overall frame and records longitudinal, evaluation, and theory gaps; no negative-evidence source reviewed yet | v1.0 |
| 005 | Verified 2026-08-26 against the Microsoft Research publication page and paper DOI | Structured tasks with known outcomes | Contradicts explanation-as-improvement assumptions and sharpens 004's evaluation gap | v1.0 |
| 006 | Verified 2026-08-26 against the paper and DOI record | Semi-structured joint activity | Extends 001's workflow redesign into explicit coordination demands; conceptual rather than deployment evidence | v1.0 |
| 007 | Verified 2026-08-26 against the PubMed record and DOI metadata | Cross-context automation reliance | Supports 003's human judgment boundary and provides a calibration lens for 005 and 009 | v1.0 |
| 008 | Verified 2026-08-26 against the Microsoft Research publication page and COLM record | Multi-agent application workflows | Demonstrates implementation feasibility but does not resolve the multi-agent outcome question | v1.0 |
| 009 | Verified 2026-08-26 against the Harvard publication page and ACM DOI | Structured AI-assisted decisions | Corroborates 005's overreliance risk and supplies direct negative evidence against explanation-only intervention | v1.0 |

## Corroboration matrix

Status meanings: **emerging** has one direct source, **corroborated** has support from
at least two independently scoped sources, and **contested** has material contrary
evidence. Absence of contradiction is not confirmation.

| Candidate pattern | 001 | 002 | 003 | 004 | Evidence from 005-009 | Current status | Repository consequence |
|---|---|---|---|---|---|---|---|
| Human-AI complementarity | supports | supports | supports | synthesizes | 005 supplies a direct team-performance test | corroborated | Keep collaboration, not replacement, as the frame. |
| Workflow redesign | supports | task-level implication | neutral | synthesizes | 006 specifies joint-activity demands | corroborated | Evaluate the surrounding workflow, not only the model response. |
| Evidence-based work allocation | neutral | direct support | compatible | compatible | 007 adds reliance calibration; no open-ended test | emerging | Treat allocation as a candidate capability and test it against consequential work. |
| Human judgment under uncertainty | compatible | supports human-only handling for difficult tasks | direct support | compatible | 007 and 009 support calibrated, deliberate reliance | corroborated | Preserve explicit human-owned judgments and escalation criteria. |
| Interaction quality as an outcome | compatible | partially measurable through performance | compatible | direct synthesis | 005 measures complementarity; 009 exposes burden trade-offs | corroborated but underspecified | Define measures before claiming improvement. |
| Longitudinal continuity | not tested | not tested | not tested | names a literature gap | 006 supplies protocol concepts but no longitudinal test | emerging research debt | Breadcrumbs may provide a test bed, but current implementation is not research validation. |
| Unified collaboration evaluation | not supplied | task-performance measure only | not supplied | names a literature gap | 005 and 009 require outcome and burden measures | emerging research debt | Do not publish one composite score as settled science. |
| Multi-AI coordination | not tested | not tested | not tested | adjacent, not resolved | 008 demonstrates framework feasibility only | unresolved | Keep as an open question, not a supported contribution. |
| Complementary team performance | implied | task allocation can support it | compatible | identifies evaluation gap | contested by 005 when explanation is treated as the intervention | contested and measurable | Compare team performance with both human-only and AI-only baselines. |
| Joint-activity protocol quality | workflow implication | compatible | compatible | identifies interaction-design need | direct challenge framework in 006 | corroborated but not operationalized | Turn coordination demands into bounded, observable protocol checks. |
| Calibrated reliance | compatible | allocation depends on capability | compatible | compatible | direct support in 007; failure evidence in 005 and 009 | corroborated | Measure reliance against demonstrated capability and consequence, not stated trust. |
| Conversational multi-agent feasibility | not tested | not tested | not tested | adjacent | demonstrated by 008 pilot applications | emerging | Treat as implementation evidence only until matched comparisons show a benefit. |
| Deliberate friction at consequential boundaries | not tested | compatible | supports human judgment | compatible | direct support with trade-offs in 009 | emerging | Test consequence-scaled review friction and track both error detection and burden. |

The second pass supplies the first direct negative evidence. Papers 005 and 009 show
that explanations and low-friction assistance can increase acceptance without improving
judgment. The next search should test whether those effects survive sustained,
open-ended work rather than returning to supportive framework papers.

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

## Adjacent-angle seed status

| Angle | Seed source | What is now known | What remains unresolved |
|---|---|---|---|
| Team evaluation | 005 | Complementarity needs human-only, AI-only, and team baselines; explanation is not an outcome. | A cross-context outcome set for quality, effort, reversibility, and accountability. |
| Durable protocols | 006 | Joint work depends on coordination properties, not task completion alone. | Observable conformance checks that survive model, tool, and session changes. |
| Calibrated reliance | 007 | Appropriate reliance, not maximum trust, is the design target. | Behavioral calibration measures for changing generative systems. |
| Multi-agent coordination | 008 | Conversation frameworks make multi-agent patterns feasible. | Matched evidence that extra agents improve outcomes rather than cost and complexity. |
| Overreliance and external validity | 009 | Deliberate cognitive friction can reduce overreliance but carries usability and equity trade-offs. | Consequence-scaled interventions tested in sustained professional work. |

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
