# Collaborative intelligence repository landscape method

**Status:** public research method. It appraises repository-visible mechanisms.
It does not certify a product, prove runtime performance, or rank frameworks.

## Research question

How do public repositories make collaborative intelligence concrete, and which
parts of claims `CI-001` through `CI-017` are directly visible, only partial,
not observed at the reviewed depth, or outside a repository's stated scope?

The comparison is not which repository has the most features. It is which
mechanisms are inspectable, bounded, testable, and honest about authority,
recovery, cost, change, and evidence.

Stars are used only to discover widely adopted candidates within an aspect.
They are volatile, reflect project age and audience size, and do not measure
quality, safety, research validity, or collaboration benefit. Every recorded
star count carries an observation date.

## Unit of appraisal

The unit is a repository snapshot, not a vendor, paper, package download count,
or current website. Every included record binds:

- the canonical public repository;
- one 40-character commit SHA and its commit date;
- a repository category and lifecycle state;
- the evidence depth reached;
- mechanism observations linked to the claim register; and
- public evidence pointers and explicit limits.

A repository update does not silently rewrite an appraisal. It creates a new
snapshot or a recorded recheck.

## Inclusion and exclusion

Include a repository when it is public, canonical for the project, contains
code or a specification relevant to at least one collaborative-intelligence
claim, and can be pinned to a reproducible revision. The first cohort is
purposive and balances orchestration runtimes, workflow and state runtimes,
protocols, memory-oriented systems, and research-driven multi-agent systems.

For a popularity-directed wave, search each aspect separately, inspect the
most-starred candidates, then deduplicate by mechanism and product lineage.
Keep a lower-starred repository when it represents a distinct mechanism that a
more popular general platform does not. Record both the selected aspect and the
screened-out alternatives so popularity cannot silently become the rubric.

Exclude or move a repository to the lineage register when it is a duplicate
fork without a distinct mechanism, a marketing-only landing page, a tutorial
without a reusable mechanism, an archived exemplar, or a superseded project
whose own repository points users to a successor. Exclusion is not a quality
judgment.

## Repository categories

- `agent-runtime`: agent loop, tools, delegation, or subagent execution.
- `workflow-runtime`: explicit graph, flow, checkpoint, or resumable state.
- `protocol`: interfaces for context, tools, tasks, or agent communication.
- `memory-runtime`: durable context, identity, retrieval, or long-horizon state.
- `retrieval-runtime`: data, indexing, graph, retrieval, or context assembly.
- `evaluation-platform`: traces, datasets, experiments, comparisons, or red teams.
- `guardrail-runtime`: programmable constraints around model or agent behavior.
- `application-control-plane`: supervises one or more agent backends in a
  concrete work surface.
- `research-framework`: research-oriented roles, societies, simulation, or
  software-process experiments.
- `model-gateway`: normalizes providers or agents while applying routing,
  access, budget, retry, or guardrail policy.
- `execution-sandbox`: isolates agent work and exposes lifecycle or human
  control outside the model loop.
- `hybrid-platform`: several of the above with no single dominant layer.

Lifecycle states remain separate from mechanism categories:

- `current`: active public implementation or specification.
- `maintenance`: retained with a visible maintenance or successor boundary.
- `research-artifact`: public implementation primarily preserved to reproduce
  or inspect a research result rather than represent a current product path.

## Evidence depth

- `identity-only`: canonical identity and lifecycle were checked.
- `readme-screened`: the README at the pinned commit was reviewed far enough
  to classify the visible mechanisms and stated boundaries.
- `mechanism-screened`: linked documentation, tests, or implementation paths
  were inspected for the named mechanism.
- `code-traced`: the mechanism was followed through its implementation and
  tests at the pinned commit.
- `executed`: a bounded local or published reproducible evaluation exercised
  the mechanism.
- `independently-reproduced`: an independent party reproduced the relevant
  result under stated conditions.

Evidence depth applies to each observation. A README feature claim remains a
README-screened observation even when the repository contains tests elsewhere.

## Observation codes

| Code | Meaning |
|---|---|
| `V` | Visible in reviewed public evidence at the stated depth |
| `P` | Partially visible, adjacent, or missing an important boundary |
| `N` | Not observed in the material reviewed at the stated depth |
| `O` | Outside the repository's stated layer or purpose |

`N` never means the mechanism is absent from the entire project. It means the
review did not observe it at the recorded depth. Only a code-traced review may
make a bounded absence claim about a named path.

## Mechanism dimensions

The machine-readable register records these dimensions separately:

1. `collaboration_topology`: roles, handoffs, subagents, teams, or task routing.
2. `workflow_state`: explicit stages, durable execution, task state, or resume.
3. `human_authority`: intervention, confirmation, permission, or approval
   boundaries that name what the human controls.
4. `memory_context`: session, retrieval, identity, or durable context handling.
5. `trace_recovery`: traces, checkpoints, replay, rollback, or recovery support.
6. `evaluation_surface`: first-party facilities for tests, evals, metrics, or
   inspection of agent or workflow behavior.
7. `collaboration_baseline`: a comparison that can test whether collaboration
   beats a relevant single-agent, no-AI, or simpler-process baseline.
8. `cost_burden`: time, compute, token, review, coordination, or human burden.
9. `change_expiry`: version and material-change handling that can invalidate
   stale evidence or state.
10. `independent_verification`: evidence from a distinct verifier rather than
    the same agent family grading its own output.
11. `interoperability`: an explicit cross-tool, cross-agent, or cross-system
    contract.

These dimensions operationalize parts of `CI-001` through `CI-017`. They do not
replace the claim register, and they are not added into one score.

## Appraisal procedure

1. Resolve the canonical repository and pin the current snapshot.
2. Classify lifecycle and category before reading feature claims.
3. Review the README and follow only the public pointers needed for the stated
   depth.
4. Record each dimension as `V`, `P`, `N`, or `O` with a short evidence note.
5. Link only the claims the reviewed evidence can reasonably inform.
6. Separate an implementation mechanism from evidence that the mechanism helps.
7. Record commercial, hosted, or companion-product boundaries explicitly.
8. Add lineage, migration, archive, and duplicate decisions to the collection
   log instead of silently dropping candidates.
9. Recheck after a material repository, product, model, policy, or data change.

## Synthesis rules

- Do not calculate a composite framework score or declare a winner.
- Feature count is not collaboration quality.
- A trace facility is not evidence that traces improved diagnosis.
- Human-in-the-loop is not a complete authority model unless the controlled
  action and consequence are visible.
- Multi-agent support is not evidence of a multi-agent advantage.
- Self-critique, debate, or another instance of the same model is not
  independent verification by default.
- Protocol conformance is not outcome quality.
- Open-source and commercial control-plane mechanisms remain separate.
- Repository evidence cannot prove private deployment behavior.

The output is a gap-directed research map. Strong claims still require the
confidence profile, contrary evidence, null case, and owning-system test defined
by [Method v2.0](collaborative-intelligence-method-v2.md).
