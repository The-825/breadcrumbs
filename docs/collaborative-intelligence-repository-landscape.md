# Collaborative intelligence repository landscape

**Status:** first public, gap-directed cohort. The observations are pinned,
README-screened repository evidence. They are not runtime tests, product
endorsements, or proof that collaboration improves outcomes.

The [method](collaborative-intelligence-repository-landscape-method.md) defines
the codes and boundaries. The
[machine-readable register](collaborative-intelligence-repository-landscape.json)
holds the exact commit, evidence note, claim links, and 11-dimension profile for
each repository.

## Cohort

| ID | Repository | Category | Snapshot | What is visibly codified | Main untested question |
|---|---|---|---|---|---|
| R-001 | [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) | agent runtime | `1749d361` | agents, guardrails, handoffs, sessions, human intervention, tracing | Do handoffs or multiple agents beat a simpler relevant baseline? |
| R-002 | [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) | hybrid platform | `de02975e` | concurrent and handoff workflows, checkpoints, human intervention, time travel, telemetry | Which topology helps which workflow after cost and review burden? |
| R-003 | [Google ADK](https://github.com/google/adk-python) | hybrid platform | `d563bdea` | graph workflows, delegation, state, retries, evals, confirmation, compatibility notices | Do the evals compare collaboration with a simpler configuration? |
| R-004 | [A2A](https://github.com/a2aproject/A2A) | protocol | `5e233e57` | discovery and task communication across opaque agents | What outcome evidence should accompany protocol conformance? |
| R-005 | [LangGraph](https://github.com/langchain-ai/langgraph) | workflow runtime | `d5f4b2aa` | durable execution, state inspection, memory, tracing, restart | Does the added orchestration improve recovery and total workflow cost? |
| R-006 | [CrewAI](https://github.com/crewAIInc/crewAI) | hybrid platform | `4bc5d292` | role-based crews and event-driven flows | Which governance and observability mechanisms are open-source versus commercial? |
| R-007 | [Model Context Protocol](https://github.com/modelcontextprotocol/modelcontextprotocol) | protocol | `d8fdc88f` | versioned context, tool, and resource contracts | How should authorization and outcome quality be evaluated above the protocol layer? |
| R-008 | [CAMEL](https://github.com/camel-ai/camel) | research framework | `e88b5eeb` | agent societies, scalability, evolvability, and statefulness | Which research results transfer to governed human workflows? |
| R-009 | [MetaGPT](https://github.com/FoundationAgents/MetaGPT) | research framework | `11cdf466` | software roles and standard operating procedures | Are role reviews independent enough to detect correlated errors? |
| R-010 | [smolagents](https://github.com/huggingface/smolagents) | agent runtime | `30bb1161` | small code-agent runtime, managed agents, sandboxing, MCP | When does a managed-agent topology outperform one agent with tools? |
| R-011 | [AgentScope](https://github.com/agentscope-ai/agentscope) | hybrid platform | `6c5c9eed` | permissions, confirmation, middleware, memory backends, workspaces | Do the controls produce measurable recovery and reliance improvements? |
| R-012 | [Letta Code](https://github.com/letta-ai/letta-code) | memory runtime | `00167017` | long-horizon memory, git-tracked context, subagents, permissions, schedules | How are self-modification, correction survival, and independent validation tested? |
| R-013 | [AG2](https://github.com/ag2ai/ag2) | hybrid platform | `5d344750` | AgentOS networks, channels, multi-agent patterns, human participation | Which network structures help after coordination cost is counted? |
| R-014 | [Pydantic AI](https://github.com/pydantic/pydantic-ai) | hybrid platform | `bed124c2` | typed loops, durable execution, evals, memory, subagents, workspace controls | Do evals isolate collaboration benefit and correlated failure? |
| R-015 | [Mastra](https://github.com/mastra-ai/mastra) | hybrid platform | `a5d916ae` | graph workflows, suspend and resume, state, memory, MCP, evals, observability | Which public mechanisms improve the full workflow rather than only task output? |

## What the first cohort says

### 1. Topology is common. Evidence of benefit is not.

Handoffs, roles, subagents, crews, graphs, channels, and agent networks are
visible across most runtime repositories. None of the 15 README-screened
snapshots visibly establishes a relevant collaboration baseline. This is a
direct implementation gap for `CI-001` and `CI-016`: supporting more agents is
not the same as showing that more agents help.

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
same-context reviewers can share failure modes. The first cohort gives little
README-level evidence that `CI-017` is handled explicitly.

### 7. Product boundaries change the appraisal.

Some repositories pair open-source runtimes with hosted or enterprise control
planes. The register records only mechanisms visible in the pinned public
repository and names the boundary when the README assigns governance,
observability, or operational features elsewhere. Public code and commercial
claims must not be blended into one result.

## Next code-traced wave

The next appraisal should not expand the cohort immediately. It should select
five contrasting repositories and trace the same four mechanisms through code,
tests, and evaluation fixtures:

1. collaboration versus a simpler baseline;
2. trace-to-recovery behavior;
3. action-specific human authority; and
4. stale-evidence or material-change invalidation.

Recommended contrasting cases are Microsoft Agent Framework, Google ADK,
A2A, Letta Code, and Pydantic AI. Together they cover orchestration, workflow
state, protocol, long-horizon memory, and typed evaluation without treating any
one architecture as the field.

## Boundary

This cohort changes the research map, not Breadcrumbs runtime claims. A visible
mechanism may become a reusable pattern only after the Method v2 promotion rule
is met, including contrary evidence, a null case, a relevant owning-system test,
and explicit change conditions.
