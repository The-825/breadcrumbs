# Collaborative intelligence repository landscape

**Status:** public, two-wave cohort of 25 repositories. The observations are pinned,
README-screened repository evidence. They are not runtime tests, product
endorsements, or proof that collaboration improves outcomes.

The [method](collaborative-intelligence-repository-landscape-method.md) defines
the codes and boundaries. The
[machine-readable register](collaborative-intelligence-repository-landscape.json)
holds the exact commit, evidence note, claim links, and 11-dimension profile for
each repository.

## Cohort

Stars were observed on 2026-08-27. They explain discovery priority, not quality.

| ID | Repository | Stars | Aspect | Snapshot | What is visibly codified |
|---|---|---:|---|---|---|
| R-001 | [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) | 29,012 | agent runtime | `1749d361` | agents, guardrails, handoffs, sessions, human intervention, tracing |
| R-002 | [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) | 13,154 | multi-agent workflow | `de02975e` | concurrent and handoff workflows, checkpoints, human intervention, time travel, telemetry |
| R-003 | [Google ADK](https://github.com/google/adk-python) | 21,310 | agent development | `d563bdea` | graph workflows, delegation, state, retries, evals, confirmation, compatibility notices |
| R-004 | [A2A](https://github.com/a2aproject/A2A) | 25,518 | agent protocol | `5e233e57` | discovery and task communication across opaque agents |
| R-005 | [LangGraph](https://github.com/langchain-ai/langgraph) | 40,568 | durable workflow | `d5f4b2aa` | durable execution, state inspection, memory, tracing, restart |
| R-006 | [CrewAI](https://github.com/crewAIInc/crewAI) | 57,688 | role orchestration | `4bc5d292` | role-based crews and event-driven flows |
| R-007 | [Model Context Protocol](https://github.com/modelcontextprotocol/modelcontextprotocol) | 9,067 | context protocol | `d8fdc88f` | versioned context, tool, and resource contracts |
| R-008 | [CAMEL](https://github.com/camel-ai/camel) | 17,650 | agent-society research | `e88b5eeb` | agent societies, scalability, evolvability, and statefulness |
| R-009 | [MetaGPT](https://github.com/FoundationAgents/MetaGPT) | 70,070 | role-process research | `11cdf466` | software roles and standard operating procedures |
| R-010 | [smolagents](https://github.com/huggingface/smolagents) | 29,022 | minimal agent runtime | `30bb1161` | code agents, managed agents, sandboxing, MCP |
| R-011 | [AgentScope](https://github.com/agentscope-ai/agentscope) | 29,822 | permissioned agents | `6c5c9eed` | permissions, confirmation, middleware, memory backends, workspaces |
| R-012 | [Letta Code](https://github.com/letta-ai/letta-code) | 3,134 | long-horizon memory | `00167017` | git-tracked context, subagents, permissions, schedules, self-modification |
| R-013 | [AG2](https://github.com/ag2ai/ag2) | 4,890 | networked agents | `5d344750` | AgentOS networks, channels, multi-agent patterns, human participation |
| R-014 | [Pydantic AI](https://github.com/pydantic/pydantic-ai) | 19,539 | typed agents | `bed124c2` | typed loops, durable execution, evals, memory, subagents, workspace controls |
| R-015 | [Mastra](https://github.com/mastra-ai/mastra) | 27,525 | TypeScript agents | `a5d916ae` | workflows, suspend and resume, state, memory, MCP, evals, observability |
| R-016 | [Dify](https://github.com/langgenius/dify) | 153,684 | visual agent workflow | `458c96d5` | visual workflows, RAG, agents, model management, observability integrations |
| R-017 | [Mem0](https://github.com/mem0ai/mem0) | 64,201 | agent memory layer | `fdfb763d` | user, session, and agent memory, temporal retrieval, benchmark cost fields |
| R-018 | [LlamaIndex](https://github.com/run-llama/llama_index) | 51,895 | data and context | `39f481fc` | connectors, indices, graphs, retrieval, queries, agent workflows |
| R-019 | [RAGFlow](https://github.com/infiniflow/ragflow) | 89,405 | agent context engine | `88e80fc5` | context engine, RAG workflows, memory, citations, MCP, sandboxing |
| R-020 | [GraphRAG](https://github.com/microsoft/graphrag) | 35,707 | graph retrieval research | `f40e9a26` | graph-structured context pipeline, research boundary, cost warning, maintenance status |
| R-021 | [DSPy](https://github.com/stanfordnlp/dspy) | 37,626 | program optimization | `3afc03f2` | modular language-model programs and prompt or weight optimization |
| R-022 | [Promptfoo](https://github.com/promptfoo/promptfoo) | 24,623 | evaluation and red team | `e3b36451` | comparison matrices, local evals, red teaming, vulnerability reports, CI review |
| R-023 | [Phoenix](https://github.com/Arize-ai/phoenix) | 11,217 | observability and experiments | `8adf3376` | tracing, versioned datasets, experiments, evaluation, replay, integrations |
| R-024 | [NeMo Guardrails](https://github.com/NVIDIA-NeMo/Guardrails) | 7,023 | programmable guardrails | `94fb1cdc` | model controls, dialog paths, output constraints, linked technical evaluation |
| R-025 | [OpenHands](https://github.com/OpenHands/OpenHands) | 85,300 | agent control plane | `b50c60c6` | multiple coding-agent backends, automations, integrations, ACP interoperability |

## What the 25-repository cohort says

### Mechanism profile at a glance

The register uses `V` for verified at the current evidence depth, `P` for
partial, `N` for not found, and `O` for out of scope. These counts summarize
the 25 pinned README-level appraisals. They are not product scores.

| Mechanism | V | P | N | O |
| --- | ---: | ---: | ---: | ---: |
| collaboration topology | 13 | 7 | 0 | 5 |
| workflow state | 15 | 10 | 0 | 0 |
| human authority | 3 | 18 | 3 | 1 |
| memory and context | 11 | 10 | 0 | 4 |
| trace and recovery | 4 | 21 | 0 | 0 |
| evaluation surface | 6 | 17 | 0 | 2 |
| collaboration baseline | 2 | 3 | 18 | 2 |
| cost and burden | 2 | 5 | 16 | 2 |
| change and expiry | 4 | 6 | 15 | 0 |
| independent verification | 0 | 3 | 20 | 2 |
| interoperability | 12 | 13 | 0 | 0 |

### 1. Topology is common. Evidence of benefit is not.

Handoffs, roles, subagents, crews, graphs, channels, and agent networks are
visible across most runtime repositories. Promptfoo and Phoenix provide ways
to compare configurations, but the orchestration repositories rarely make a
single-agent or simpler-process baseline part of the collaboration mechanism.
This keeps `CI-001` and `CI-016` open: supporting more agents is not the same as
showing that more agents help.

### 2. State and observability are becoming infrastructure.

Durable state, checkpoints, traces, telemetry, or resumable workflows appear in
many repositories. The gap is causal. A trace facility does not show that a
team diagnosed failures faster, recovered more reliably, or reduced repeated
work. A later code-traced wave should inspect whether evaluation suites measure
those outcomes under `CI-002` and `CI-006`.

### 3. Human intervention is visible, but authority is often underspecified.

Confirmation, suspension, approval, and permission controls appear regularly.
README-level evidence rarely states a complete function-specific authority
model with consequences, expiry, and recovery expectations. This keeps
`CI-007`, `CI-011`, and `CI-013` open even where a human-in-the-loop feature is
visible.

### 4. Protocols solve a different layer.

A2A and MCP make cross-system interaction more concrete. They should not be
scored as incomplete agent runtimes. Their open research question is what
evidence travels with an interoperable task, tool, context, or agent so that a
consumer can judge authority, freshness, cost, and outcome quality.

### 5. Memory has moved into the collaboration stack.

Sessions, state stores, retrieval, durable context, and agent identity are no
longer isolated memory-system concerns. They shape handoffs and long-horizon
coordination. Repository-visible support remains uneven for custody,
correction survival, deletion, stale-evidence expiry, and query-specific
retrieval evaluation under `CI-008`, `CI-009`, `CI-010`, and `CI-014`.

### 6. Independence is the weakest visible mechanism.

Role separation, critique, review, and subagents can improve process structure.
They do not automatically create an independent verifier. Same-model or
same-context reviewers can share failure modes. The 25-repository cohort gives
little README-level evidence that `CI-017` is handled explicitly. Evaluation
platforms can host a distinct test, but the operator must still establish
evaluator and evidence independence.

### 7. Product boundaries change the appraisal.

Some repositories pair open-source runtimes with hosted or enterprise control
planes. The register records only mechanisms visible in the pinned public
repository and names the boundary when the README assigns governance,
observability, or operational features elsewhere. Public code and commercial
claims must not be blended into one result.

### 8. Popularity concentrates in broad assembly surfaces.

The largest star counts in the screened set belong to broad workflow, agent,
context, and control-plane projects. Specialized authority, guardrail, and
observability repositories are smaller. This is an adoption pattern, not a
confidence profile. Stars favor projects with large audiences and wide scopes,
so they cannot decide which mechanism deserves promotion.

### 9. Evaluation infrastructure is more mature than collaboration evaluation.

Promptfoo, Phoenix, DSPy, and the benchmark surfaces in Mem0 make comparisons,
versioned datasets, experiments, and cost fields more concrete. They provide
parts of the missing measurement plane. They do not automatically identify the
right human-AI baseline, coordination burden, recovery outcome, or independent
verifier for a specific workflow.

### 10. Retrieval systems expose costs and boundaries more often.

Mem0 records tokens and latency while distinguishing managed optimizations from
the open SDK. GraphRAG warns that indexing is expensive and labels itself a
maintenance-mode research demonstration. These are stronger evidence-honesty
signals than silent feature lists, but they still do not establish transfer to
a governed collaborative workflow.

## Next code-traced wave

The next appraisal should not expand the cohort immediately. It should select
six contrasting repositories and trace the same four mechanisms through code,
tests, and evaluation fixtures:

1. collaboration versus a simpler baseline;
2. trace-to-recovery behavior;
3. action-specific human authority; and
4. stale-evidence or material-change invalidation.

Recommended contrasting cases are Microsoft Agent Framework, A2A, Letta Code,
Mem0, Promptfoo, and OpenHands. Together they cover orchestration, protocol,
long-horizon memory, explicit benchmark costs, independent test infrastructure,
and an application control plane without treating any one architecture as the
field.

## Boundary

This cohort changes the research map, not Breadcrumbs runtime claims. A visible
mechanism may become a reusable pattern only after the Method v2 promotion rule
is met, including contrary evidence, a null case, a relevant owning-system test,
and explicit change conditions.
