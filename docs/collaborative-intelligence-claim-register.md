# Collaborative intelligence claim register

**Method:** [v2.0](collaborative-intelligence-method-v2.md)

**Status:** public research synthesis. These claims shape questions and methods.
They do not certify a Breadcrumbs runtime or authorize an external action.

## Reading the register

Source IDs resolve through the
[research ledger](collaborative-intelligence-research-ledger.md). Profiles list
`directness / validity / independence / consistency / transfer / durability`.
The 001 through 100 source pass is screened, not a complete full-text
risk-of-bias review. Validity therefore remains bounded even when a design looks
strong from the reviewed record.

## Active claims

### CI-001: Collaboration benefit is conditional

**Claim.** Human-AI or multi-agent collaboration should be treated as beneficial
only when it beats the best relevant individual or established-workflow baseline
on the outcome that matters for the bounded task.

- **Supports:** 001, 002, 010, 013, 018, 019, 023, 039, 085
- **Contrary or limiting evidence:** 005, 011, 014, 020, 022, 024, 042
- **Profile:** high / not fully appraised / high / contested / bounded / repeated
- **Disposition:** `adopt-method`
- **Null case:** the cooperative condition does not beat the better baseline, or
  gains disappear when quality, cost, burden, or safety is included.
- **Next test:** compare no-AI, one-agent, and cooperative modes on the same
  unseen work item with equal outcome definitions and observed cost.

### CI-002: Evaluate stages and workflow, not only final output

**Claim.** Generation, selection, review, correction, handoff, and closeout can
have different owners and outcomes, so one final-output measure cannot establish
collaboration quality.

- **Supports:** 001, 003, 004, 006, 012, 013, 017, 025, 030, 058, 090-092
- **Limits:** most agent evidence uses benchmarks or short workflows.
- **Profile:** moderate / not fully appraised / high / convergent / bounded / repeated
- **Disposition:** `adopt-method`
- **Null case:** stage measures add no explanatory or corrective value beyond
  final outcome and only increase burden.
- **Next test:** identify the stage at which an observed gain, failure, or
  correction entered the work.

### CI-003: Appropriate reliance is behavioral and dynamic

**Claim.** Trust, adoption, confidence, explanation presence, and stated
preference are not substitutes for observed appropriate reliance across changing
outcomes.

- **Supports:** 005, 007, 009, 015, 021, 033-037, 041, 057, 064-072, 078
- **Contrary context:** 066 and 068 show both aversion and appreciation; 067 shows
  that bounded control can change use.
- **Profile:** high / not fully appraised / high / mixed / bounded / repeated
- **Disposition:** `adopt-method`
- **Null case:** a stated-trust measure predicts correct acceptance, rejection,
  escalation, and correction as well as behavioral measures.
- **Next test:** record acceptance, verification, override, escalation, and
  recovery after both correct and incorrect assistance.

### CI-004: Collaboration process has a cost

**Claim.** Added roles, messages, explanations, and review steps can reduce
quality, throughput, independence, or willingness to engage even when intended
as safeguards.

- **Supports:** 009, 011, 014, 021, 024, 026, 042, 072, 074
- **Limits:** burden measures are inconsistent across studies.
- **Profile:** moderate / not fully appraised / moderate / convergent / bounded / single-task
- **Disposition:** `adopt-method`
- **Null case:** the protocol improves the named outcome with no material time,
  burden, or independence cost.
- **Next test:** record messages, elapsed time, active work, review burden, and
  post-handoff independence.

### CI-005: Capability is task and context specific

**Claim.** Model or agent capability should be represented for a current task
region, participant population, tool configuration, and time period rather than
as one provider-level property.

- **Supports:** 002, 018-024, 032, 038-042, 069, 093
- **Contrary or limiting evidence:** apparently similar tasks can fall on
  different sides of the useful frontier.
- **Profile:** high / not fully appraised / high / mixed / bounded / repeated
- **Disposition:** `adopt-method`
- **Null case:** one stable capability label predicts performance across the
  relevant task and version changes.
- **Next test:** define pre-action task signals and invalidate them after material
  model, tool, prompt, policy, or data changes.

### CI-006: Process traces improve failure attribution and recovery

**Claim.** Privacy-minimal stage, action, evidence, and recovery traces can expose
failures that final success or failure hides.

- **Supports:** 006, 025, 027-031, 056, 075, 090
- **Limits:** benchmark traces may not transfer to private, consequential work.
- **Profile:** moderate / not fully appraised / moderate / convergent / narrow / technical-only
- **Disposition:** `prototype`
- **Null case:** the trace does not improve attribution, correction, or replay
  enough to justify its privacy and operational cost.
- **Next test:** compare failure diagnosis with final-output evidence versus a
  redacted complete trace.

### CI-007: Authority must be bound to function and consequence

**Claim.** Information acquisition, analysis, recommendation, decision, and
action require separate authority boundaries; one agent-wide autonomy level is
not sufficient.

- **Supports:** 029, 031-033, 061-063, 070-071, 078-079
- **Limits:** foundational automation evidence predates current agent systems.
- **Profile:** moderate / not fully appraised / high / convergent / bounded / repeated
- **Disposition:** `adopt-method`
- **Null case:** a single autonomy level preserves the same safety, clarity, and
  recovery across all functions.
- **Next test:** evaluate each function separately and require action-time
  approval for consequential mutations.

### CI-008: Prior evidence expires after material change

**Claim.** Reliance, delegation, compatibility, and workflow evidence must be
revalidated after material changes to models, prompts, tools, policy, data, task,
or participant expertise.

- **Supports:** 012, 015, 027, 034-040, 043, 065, 081
- **Limits:** exact invalidation thresholds are not established.
- **Profile:** moderate / not fully appraised / moderate / convergent / bounded / repeated
- **Disposition:** `adopt-method`
- **Null case:** the prior result remains calibrated after the named change.
- **Next test:** maintain a change manifest and run a targeted replay before
  reusing prior routing evidence.

### CI-009: Effective memory is broader than recall

**Claim.** Memory evaluation must separate retrieval, updates, abstention,
temporal and causal reasoning, role, efficiency, capacity, provenance,
correction, custody, isolation, and deletion.

- **Supports:** 043-047, 051, 053, 094-100
- **Limits:** technical benchmarks do not validate repository governance.
- **Profile:** moderate / not fully appraised / high / convergent / narrow / technical-only
- **Disposition:** `adopt-method`
- **Null case:** recall or context-window performance predicts correction,
  authority, and deletion behavior in the owning system.
- **Next test:** run a repository-derived memory exam with source precedence,
  correction survival, tombstones, isolation, and stale-context rejection.

### CI-010: Grounding should be sufficient and privacy-minimal

**Claim.** Participants need shared objective, constraints, ownership, and
correction state, but do not need universal access to all source content.

- **Supports:** 006, 052-058, 089
- **Limits:** most evidence concerns human teams or conceptual frameworks.
- **Profile:** low / not fully appraised / high / convergent / bounded / repeated
- **Disposition:** `prototype`
- **Null case:** the compact grounding record does not reduce wrong-premise work
  or requires copying protected source content.
- **Next test:** compare a bounded handoff packet with transcript-scale context on
  orientation accuracy, privacy exposure, and repair cost.

### CI-011: Human authority requires visible mode and recovery readiness

**Claim.** Nominal takeover or review authority is not meaningful when mode,
routing, or system state is hidden or the human cannot recover after routine
automation.

- **Supports:** 035, 059-065
- **Limits:** direct generative-agent field evidence remains sparse.
- **Profile:** low / not fully appraised / high / convergent / bounded / repeated
- **Disposition:** `adopt-method`
- **Null case:** routine reliability alone predicts safe intervention and
  recovery.
- **Next test:** expose current mode and run a safe reentry or stale-context drill.

### CI-012: Explanation must target a named behavior

**Claim.** An explanation should be evaluated against a specified behavior, such
as error detection, correction, escalation, or appropriate reliance, rather than
confidence, preference, or explanation presence.

- **Supports:** 005, 009, 021, 037, 072-079
- **Contrary or limiting evidence:** transparency can increase confidence or
  simulability without improving correction.
- **Profile:** high / not fully appraised / high / contested / bounded / single-task
- **Disposition:** `adopt-method`
- **Null case:** explanation presence alone improves the named behavior without
  increasing bias or burden.
- **Next test:** predeclare one behavioral target and measure side effects.

### CI-013: Deferral evidence must be calibrated and expiring

**Claim.** Routing to a person, model, or specialist is justified only for the
current task region, expert, option coverage, and distribution, with abstention
and escalation preserved.

- **Supports:** 002, 038-042, 080-085
- **Limits:** evidence is strongest for structured tasks with observable labels.
- **Profile:** moderate / not fully appraised / high / convergent / narrow / single-task
- **Disposition:** `prototype`
- **Null case:** an uncalibrated or permanent routing rule performs as well after
  expert or distribution change.
- **Next test:** create an expiring deferral record and test delayed,
  multidimensional, and disputed outcomes.

### CI-014: Retrieval architecture must match the query

**Claim.** Lexical, dense, adaptive, hierarchical, graph, and long-context
approaches solve different retrieval problems and must preserve links to
versioned leaf evidence.

- **Supports:** 043-047, 051, 094-100
- **Limits:** benchmark gains do not establish source authority or correction.
- **Profile:** moderate / not fully appraised / high / convergent / narrow / technical-only
- **Disposition:** `prototype`
- **Null case:** one retrieval mode performs equivalently across local, global,
  temporal, update, and association queries while preserving governance.
- **Next test:** compare retrieval modes on the same repository-derived query set
  with provenance and tombstone checks.

### CI-015: Average quality can hide portfolio diversity loss

**Claim.** Repeated AI assistance can improve average item quality while reducing
the diversity or resilience of the collective output portfolio.

- **Supports:** 013, 017, 086, 088
- **Limits:** direct evidence is narrow and mostly short-horizon.
- **Profile:** moderate / not fully appraised / low / sparse / narrow / single-task
- **Disposition:** `watch`
- **Null case:** assisted and unassisted portfolios have equivalent diversity and
  downstream option value at matched quality.
- **Next test:** measure semantic and strategic diversity across a repeated
  research or design portfolio.

### CI-016: More agents are not a general advantage

**Claim.** Additional agents should be added only when a task-specific,
equal-cost comparison shows that decomposition, topology, or independent
information improves the bounded outcome.

- **Supports:** 024-026, 087-093
- **Contrary or limiting evidence:** selected benchmarks show gains, losses,
  judge bias, and architecture-specific effects.
- **Profile:** moderate / not fully appraised / moderate / contested / narrow / technical-only
- **Disposition:** `adopt-method`
- **Null case:** multi-agent work consistently beats one strong agent under equal
  cost on unseen, nonparallel tasks.
- **Next test:** use mature-repository holdouts, equal budgets, and an independent
  evaluator.

### CI-017: Self-refinement is not independent verification

**Claim.** Reflection, critique, debate, or iterative revision by the same model
family may improve an output but cannot independently verify a durable claim,
correction, or authority change.

- **Supports:** 048-050, 087-088, 097
- **Limits:** independence varies by model, evidence source, and evaluator.
- **Profile:** moderate / not fully appraised / moderate / convergent / bounded / technical-only
- **Disposition:** `adopt-method`
- **Null case:** same-model critique detects material errors at the same rate as
  an independent source, tool, or reviewer.
- **Next test:** compare same-model refinement with evidence-bound independent
  verification.

## Promotion summary

- **Method-shaping now:** CI-001 through CI-005, CI-007 through CI-009,
  CI-011, CI-012, CI-016, and CI-017.
- **Bounded prototypes:** CI-006, CI-010, CI-013, and CI-014.
- **Watch:** CI-015.
- **Runtime claims:** none.
- **New memory store:** none.
