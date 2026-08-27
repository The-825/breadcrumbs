# Collaborative intelligence source appraisals

**Method:** [v2.0](collaborative-intelligence-method-v2.md)

**Scope:** second-pass appraisal of sources 001 through 100. Each row is
`screened`, not a complete full-text risk-of-bias assessment. Existing findings
remain in the [source ledger](collaborative-intelligence-research-ledger.md).

Directness codes are defined in Method v2.0. Evidence-family labels flag possible
shared lineage or method, not proven dependence. `Single` means one bounded task
or short study, `repeated` means multiple interactions, `longitudinal` means use
across a meaningful period, `technical` means benchmark or system evaluation,
and `not observed` means the source does not measure behavior over time.

| ID | Design and publication state | Directness | Evidence family | Horizon | Visible risk or transfer flags | Linked claims |
|---|---|---|---|---|---|---|
| 001 | Practitioner synthesis with organizational cases | D1 analog | ORG-SYN | not observed | non-systematic selection; reported company evidence | CI-001, CI-002 |
| 002 | Journal analytical model plus experiment | D2 adjacent | ALLOCATION | single | structured classification; modeled assumptions | CI-001, CI-005, CI-013 |
| 003 | Journal conceptual synthesis | D0 conceptual | ORG-SYN | not observed | no direct test; organizational transfer | CI-001, CI-002 |
| 004 | Journal systematic literature review | D1 analog | ORG-SYN | not observed | review quality not fully appraised; broad construct variation | CI-001, CI-002, CI-003, CI-008 |
| 005 | Conference mixed-method user experiments | D2 adjacent | BANSAL-TEAM | single | structured datasets; explanation-specific intervention | CI-001, CI-003, CI-012 |
| 006 | Journal conceptual joint-activity framework | D0 conceptual | JOINT-ACTIVITY | not observed | classical automation transfer; no protocol trial | CI-002, CI-006, CI-010 |
| 007 | Journal multidisciplinary review | D1 analog | TRUST-REL | not observed | pre-LLM evidence; construct heterogeneity | CI-003 |
| 008 | Conference framework with pilot applications | D2 adjacent | MSR-AGENTS | technical | builder-evaluated; no matched best baseline | CI-016 |
| 009 | Journal experiment with 199 participants | D2 adjacent | RELIANCE-FRICTION | single | bounded decision tasks; intervention burden | CI-003, CI-004, CI-012 |
| 010 | Journal preregistered systematic review and meta-analysis | D3 target-like | SYNERGY-META | not observed | heterogeneous tasks and interventions; publication bias possible | CI-001 |
| 011 | Preprint field experiment with 388 employees | D3 target-like | MSR-WORK | single | preprint; reported confounds; one organization | CI-004 |
| 012 | Working paper, 6-month randomized field experiment | D3 target-like | MSR-WORK | longitudinal | working paper; coordination outcome coverage limited | CI-002, CI-004, CI-008 |
| 013 | Journal preregistered professional field experiment | D3 target-like | FIELD-TEAM | single | one workday; innovation-task transfer | CI-002, CI-015 |
| 014 | Journal preregistered online experiments | D2 adjacent | MOTIVATION | repeated | short sequence; online-task transfer | CI-002, CI-004 |
| 015 | Journal experiments with repeated judgments | D2 adjacent | FEEDBACK-LOOP | repeated | perceptual and social-task transfer | CI-003, CI-008, CI-017 |
| 016 | Journal reliability analysis of 52 clinical studies | D2 adjacent | CLINICAL-TEAM | not observed | healthcare specialization; interaction-order heterogeneity | CI-002, CI-003 |
| 017 | Preprint randomized marketing field experiments | D3 target-like | FIELD-TEAM | single | preprint; domain and trait-manipulation transfer | CI-001, CI-002, CI-016 |
| 018 | Journal staggered workplace deployment study | D3 target-like | FIELD-PROD | longitudinal | selection and rollout confounding; support-work domain | CI-001, CI-005 |
| 019 | Journal preregistered professional writing experiment | D3 target-like | FIELD-PROD | single | short writing tasks; no maintenance outcome | CI-001, CI-005 |
| 020 | Journal preregistered consultant field experiment | D3 target-like | FIELD-PROD | single | one occupation; frontier defined by tested model and tasks | CI-005 |
| 021 | Conference self-report survey of knowledge workers | D2 adjacent | MSR-WORK | retrospective | self-report; selection and recall bias | CI-003, CI-012 |
| 022 | Practitioner report of randomized mature-repository trial | D3 target-like | DEV-PROD | repeated | small participant count; early-2025 tools; open-source setting | CI-001, CI-005 |
| 023 | Preprint, three enterprise developer field experiments | D3 target-like | MSR-WORK | longitudinal | preprint; pooled organization and adoption effects | CI-001, CI-005 |
| 024 | Industry research benchmark across agent configurations | D2 adjacent | AGENT-SCALE | technical | benchmark transfer; configuration selection; judge dependence | CI-005, CI-016 |
| 025 | Conference interactive multi-agent benchmark | D2 adjacent | AGENT-EVAL | technical | scenario and topology dependence; no mature-repository field test | CI-006, CI-016 |
| 026 | Preprint critical analysis plus cost-aware benchmark work | D2 adjacent | AGENT-EVAL | technical | preprint; benchmark and cost-definition dependence | CI-001, CI-004, CI-006, CI-016 |
| 027 | Conference synthetic long-conversation benchmark | D2 adjacent | AGENT-EVAL | technical | synthetic conversations; model-version sensitivity | CI-006, CI-008 |
| 028 | Conference benchmark of 220 annotated agent failure traces | D2 adjacent | AGENT-EVAL | technical | trace sampling and annotator dependence; benchmark systems | CI-006 |
| 029 | Conference dynamic prompt-injection benchmark | D2 adjacent | AGENT-SECURITY | technical | simulated content and tools; defense coverage changes quickly | CI-006, CI-007 |
| 030 | Conference multi-domain agent benchmark | D2 adjacent | AGENT-EVAL | technical | benchmark and process-metric construct validity | CI-006 |
| 031 | Conference executable desktop benchmark | D2 adjacent | AGENT-EVAL | technical | environment and model versions age quickly | CI-006, CI-007 |
| 032 | Journal conceptual automation taxonomy | D0 conceptual | AUTO-HF | not observed | pre-LLM taxonomy; no direct authority trial | CI-007 |
| 033 | Journal multidisciplinary conceptual review | D1 analog | AUTO-HF | not observed | classical automation transfer; heterogeneous domains | CI-003, CI-007 |
| 034 | Journal systematic review of trust evidence | D1 analog | TRUST-REL | not observed | evidence ends in 2013; trust constructs vary | CI-003 |
| 035 | Journal narrative review and conceptual synthesis | D1 analog | TRUST-REL | not observed | no direct generative-agent test | CI-003, CI-011 |
| 036 | Journal laboratory repeated-trial experiment | D1 analog | TRUST-REL | repeated | small sample; aided-recognition task | CI-003 |
| 037 | Journal systematic review of automation bias | D1 analog | TRUST-REL | not observed | healthcare-heavy and pre-LLM evidence | CI-003, CI-012 |
| 038 | Preprint randomized delegation study | D2 adjacent | DELEGATION | repeated | preprint; content-moderation labels; induced distribution shift | CI-005, CI-008, CI-013 |
| 039 | Preprint formal team-optimization work plus experiments | D2 adjacent | ALLOCATION | technical | known-label tasks; modeled human behavior | CI-001, CI-005, CI-013 |
| 040 | Conference model-update experiments | D2 adjacent | BANSAL-TEAM | repeated | structured advice tasks; author-family overlap | CI-008 |
| 041 | Conference controlled mental-model experiments | D2 adjacent | BANSAL-TEAM | single | structured classification; author-family overlap | CI-003, CI-005 |
| 042 | Conference formal team-utility modeling plus experiments | D2 adjacent | BANSAL-TEAM | single | utility assumptions; structured high-stakes datasets | CI-001, CI-004, CI-013 |
| 043 | Conference curated long-term-memory benchmark | D2 adjacent | MEM-EVAL | technical | generated histories; benchmark and model-judge dependence | CI-008, CI-009 |
| 044 | Conference long-conversation memory benchmark | D2 adjacent | MEM-EVAL | technical | generated and human-edited dialogues; no repository custody | CI-009 |
| 045 | Conference multidimensional memory benchmark | D2 adjacent | MEM-EVAL | technical | benchmark construct choices; no governance evaluation | CI-009 |
| 046 | Preprint memory architecture demonstration | D2 adjacent | MEM-ARCH | technical | builder-evaluated; architecture demo; no authority semantics | CI-009, CI-014 |
| 047 | Conference memory architecture evaluation | D2 adjacent | MEM-ARCH | technical | simulated users; anthropomorphic retention model | CI-009 |
| 048 | Conference simulated-agent study with human ratings | D2 adjacent | SELF-REFINE | technical | simulation; believability outcome; model-judge and rater dependence | CI-009, CI-017 |
| 049 | Conference benchmark study of stored verbal feedback | D2 adjacent | SELF-REFINE | technical | benchmark transfer; same-system reflection | CI-017 |
| 050 | Conference iterative self-feedback benchmark study | D2 adjacent | SELF-REFINE | technical | same-model critique; task and judge dependence | CI-017 |
| 051 | Preprint builder evaluation of production memory system | D2 adjacent | MEM-ARCH | technical | builder-authored; benchmark and model-judge dependence | CI-009, CI-014 |
| 052 | Book chapter theory and empirical synthesis | D1 analog | TEAM-COG | not observed | human communication; medium and task transfer | CI-010 |
| 053 | Book chapter conceptual synthesis | D0 conceptual | TEAM-COG | not observed | human-group analogy; no AI test | CI-009, CI-010 |
| 054 | Journal scale development and laboratory-field validation | D1 analog | TEAM-COG | repeated | human-team self-report scale; direct transfer rejected | CI-010 |
| 055 | Journal methodological review of team knowledge | D1 analog | TEAM-COG | not observed | human-team measures; construct heterogeneity | CI-010 |
| 056 | Journal theoretical teamwork synthesis | D0 conceptual | TEAM-COG | not observed | no direct agent-team validation | CI-006, CI-010 |
| 057 | Journal field study of 51 work teams | D1 analog | TEAM-COG | repeated | observational team evidence; organizational confounding | CI-003, CI-010 |
| 058 | Journal theoretical distributed-cognition framework | D0 conceptual | TEAM-COG | not observed | framework-level transfer; no intervention test | CI-002, CI-010 |
| 059 | Journal foundational analysis of automated supervision | D1 analog | AUTO-HF | not observed | process-control domain; historical technology | CI-011 |
| 060 | Journal laboratory automation-level experiment | D1 analog | AUTO-HF | repeated | laboratory control task; historical interface | CI-011 |
| 061 | Journal mode-awareness analysis | D1 analog | AUTO-HF | not observed | supervisory-control domain; no current agent trial | CI-007, CI-011 |
| 062 | Journal synthesis of automation and autonomy evidence | D1 analog | AUTO-HF | not observed | broad review; current-agent transfer untested | CI-007, CI-011 |
| 063 | Journal meta-analysis of 18 automation experiments | D1 analog | AUTO-HF | not observed | classical automation studies; heterogeneous stages | CI-007, CI-011 |
| 064 | Journal meta-analysis of 29 human-robot studies | D1 analog | TRUST-REL | not observed | robot interaction; trust is not reliance | CI-003 |
| 065 | Journal integrative longitudinal trust model | D1 analog | TRUST-REL | longitudinal | theoretical integration; robot-team transfer | CI-003, CI-008 |
| 066 | Journal series of incentivized forecasting experiments | D2 adjacent | ALGO-USE | single | forecasting tasks; observed-error framing | CI-003 |
| 067 | Journal incentivized forecasting experiments | D2 adjacent | ALGO-USE | single | limited numeric edits; use is not correctness | CI-003 |
| 068 | Journal advice-taking experiments | D2 adjacent | ALGO-USE | single | short judgment tasks; novice-expert framing | CI-003 |
| 069 | Journal laboratory and field experiments | D2 adjacent | ALGO-USE | single | consumer and marketing settings; framing sensitivity | CI-003, CI-005 |
| 070 | Conference controlled risk-assessment experiment | D2 adjacent | FAIRNESS-HCAI | single | constructed decision setting; subgroup transfer | CI-003, CI-013 |
| 071 | Journal experiment across pretrial and loan contexts | D2 adjacent | FAIRNESS-HCAI | single | hypothetical decisions; policy-value sensitivity | CI-003, CI-007 |
| 072 | Conference preregistered experiments with 3,800 participants | D2 adjacent | XAI-BEHAVIOR | single | synthetic prediction tasks; interpretability manipulation | CI-003, CI-012 |
| 073 | Conference synthesis, expert review, and scenario validation | D1 analog | XAI-GUIDANCE | not observed | guideline coverage is not outcome evidence | CI-012 |
| 074 | Conference user study of interpretability tools | D2 adjacent | XAI-BEHAVIOR | single | data-scientist sample; tool-specific misunderstandings | CI-004, CI-012 |
| 075 | Conference interviews with speculative scenario | D1 analog | XAI-GUIDANCE | single | small qualitative sample; proposed design not deployed | CI-006, CI-012 |
| 076 | Journal interdisciplinary literature review | D1 analog | XAI-GUIDANCE | not observed | selective synthesis; no single interface test | CI-012 |
| 077 | Preprint selective survey and conceptual synthesis | D0 conceptual | XAI-GUIDANCE | not observed | preprint; selective coverage; no direct outcome test | CI-012 |
| 078 | Conference formal and sociological analysis | D0 conceptual | TRUST-REL | not observed | formalization without complete measurement instrument | CI-003, CI-007, CI-012 |
| 079 | Journal conceptual human-centered AI framework | D0 conceptual | XAI-GUIDANCE | not observed | framework-level claims; no direct validation | CI-007, CI-012 |
| 080 | Conference formal framework with synthetic decision makers | D2 adjacent | DEFER | technical | synthetic experts; fairness objective choices | CI-013 |
| 081 | Conference theoretical estimator plus benchmarks | D2 adjacent | DEFER | technical | structured labels; historical expert behavior | CI-008, CI-013 |
| 082 | Conference multi-expert framework with synthetic and crowd data | D2 adjacent | DEFER | technical | constructed experts; content-moderation transfer | CI-013 |
| 083 | Conference calibration theory plus experiments | D2 adjacent | DEFER | technical | classification benchmarks; delayed outcomes absent | CI-013 |
| 084 | Conference conformal support with simulated and real predictions | D2 adjacent | DEFER | technical | bounded option sets; outcome observability required | CI-013 |
| 085 | Conference theoretical complementarity and fairness analysis | D1 analog | DEFER | not observed | modeled losses and groups; no open-ended workflow | CI-001, CI-013 |
| 086 | Journal preregistered story-writing experiment | D2 adjacent | PORTFOLIO-DIVERSITY | single | one creative domain; short horizon | CI-015 |
| 087 | Preprint multiagent-debate benchmarks | D2 adjacent | MULTIAGENT | technical | preprint; same-model instances; judge dependence | CI-016, CI-017 |
| 088 | Conference debate experiments | D2 adjacent | MULTIAGENT | technical | narrow tasks; judge bias and degeneration | CI-015, CI-016, CI-017 |
| 089 | Conference role-playing framework and studies | D2 adjacent | MULTIAGENT | technical | generated tasks; sustained conversation is not success | CI-010, CI-016 |
| 090 | Conference software-agent framework and benchmarks | D2 adjacent | MULTIAGENT | technical | simulated organization; builder-evaluated artifacts | CI-002, CI-006, CI-016 |
| 091 | Conference staged software-agent framework | D2 adjacent | MULTIAGENT | technical | generated software tasks; production transfer absent | CI-002, CI-016 |
| 092 | Conference multi-agent framework and simulations | D2 adjacent | MULTIAGENT | technical | emergence and simulation outcomes; limited governance | CI-002, CI-016 |
| 093 | Conference dynamic-team benchmark experiments | D2 adjacent | MULTIAGENT | technical | benchmark contribution scores; version sensitivity | CI-005, CI-016 |
| 094 | Conference retrieval-plus-generation benchmarks | D2 adjacent | RETRIEVAL | technical | Wikipedia tasks; retrieval is not entailment | CI-009, CI-014 |
| 095 | Conference dense-retrieval benchmarks | D2 adjacent | RETRIEVAL | technical | open-domain QA; recall is not answer validity | CI-014 |
| 096 | Journal controlled long-context benchmarks | D2 adjacent | RETRIEVAL | technical | model and layout sensitivity; synthetic key-value task | CI-009, CI-014 |
| 097 | Conference adaptive retrieval and self-critique benchmarks | D2 adjacent | RETRIEVAL | technical | learned critique is not independent validation | CI-014, CI-017 |
| 098 | Conference hierarchical retrieval benchmarks | D2 adjacent | RETRIEVAL | technical | generated summaries may distort leaf evidence | CI-009, CI-014 |
| 099 | Conference graph-retrieval benchmarks | D2 adjacent | RETRIEVAL | technical | multi-hop QA; biological analogy; no tombstones | CI-009, CI-014 |
| 100 | Preprint builder evaluation of graph summarization | D2 adjacent | RETRIEVAL | technical | builder-authored; model-generated graphs and judges | CI-009, CI-014 |

## Re-evaluation result

The backfill changes the interpretation of the collection in four ways.

1. The 100 sources represent 17 active claim areas, not 100 independent votes.
2. Direct target-like evidence is concentrated in bounded productivity and field
   studies. Memory, retrieval, and multi-agent claims rely heavily on technical
   benchmarks.
3. Foundational automation and team-cognition evidence is useful but analogical.
   It must become a test requirement rather than a claim that current agent
   systems behave identically.
4. The collection contains meaningful contrary evidence, but it is not a
   systematic review. Search completeness, inaccessible full text, publication
   bias, shared datasets, and author-family dependence remain unresolved.

No source was promoted to `full-text` or `replicated` during this structural
backfill. No original finding was silently rewritten.
