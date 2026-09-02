# Collaborative intelligence repository collection log

## 2026-08-29: public assessment transfer

### Hardened reconciliation

The producer contract 2.0 transfer contains 225 assessment sources representing
223 positively public-verified repositories. Two duplicate assessments collapse
inside the transfer. Twelve repositories match the 100-record detailed landscape
through canonical keys or evidence-backed aliases, and 211 remain portable-only.
The reconciled public ledger therefore contains 311 unique repositories.

### Wave R4 detailed-review promotion

One hundred six of those portable identities now have pinned, README-screened
mechanism appraisals. The promotion preserves each hardened transfer source,
stable identity, alias, source revision, content hash, and evidence-only authority.
The public ledger remains 311 repositories: 206 detailed appraisals and 105
portable-only records. A record that is not promoted remains in discovery intake;
triage never deletes a positively verified public identity from the ledger.

One candidate from the earlier transfer is now aggregate-only. Independent public
GitHub verification did not establish that it met the positive-public contract,
so its identity is not published. The producer also excludes 19 supporting-only
references, four unresolved identities, and nine operated repositories.

### Initial transfer history

**Mode:** deterministic public-only import into the existing repository
landscape.

The initial transfer contained 226 assessment sources representing 224 public
repositories. Two duplicates collapsed inside the transfer, ten repositories
matched the existing 100-record landscape, and 214 new identities entered the
ledger. The result is 314 unique assessed repositories.

Operated repositories, private portfolio identities, internal paths, and
private evidence were excluded before import. Nineteen supporting-only
references, four unresolved identities, and nine operated repositories are
reported only as aggregate exclusions. Portable records carry evidence-only provenance
and cannot install software, grant authority, create work, or inherit a
detailed mechanism review.

## Wave R1, 2026-08-27

**Mode:** purposive, gap-directed landscape scan.

**Question:** How do public repositories make collaborative intelligence
concrete, and which parts of claims `CI-001` through `CI-017` are visible at a
pinned public revision?

**Sources searched:** canonical public GitHub repositories and their pinned
README files. Repository identity, archive state, default branch, and current
commit were checked through GitHub's public API.

**Selection goal:** cover agent runtimes, workflow and state runtimes,
interoperability protocols, memory-oriented systems, and research-driven
multi-agent systems. The scan favors mechanism diversity over popularity.

**Included:** 15 repositories. Every included record has a unique canonical
repository, a 40-character commit SHA, a commit date, a category, a lifecycle
state, a README-screened evidence note, claim links, and an 11-dimension
mechanism profile.

**Known limits:** this is not an exhaustive repository search, security audit,
dependency review, full code appraisal, execution benchmark, or independent
reproduction. README feature claims were not promoted to runtime proof.

## Lineage, archive, and deferral decisions

| Candidate | Snapshot | Decision | Reason |
|---|---|---|---|
| [microsoft/autogen](https://github.com/microsoft/autogen) | `027ecf0a` | lineage | Its README states maintenance mode and directs new users to Microsoft Agent Framework. It remains historically important but is not treated as an equal current target. |
| [letta-ai/letta](https://github.com/letta-ai/letta) | `4511fa0b` | lineage | The repository is now a landing page and points current source work to Letta Code. The current implementation target is `letta-ai/letta-code`. |
| [langchain-ai/open_deep_research](https://github.com/langchain-ai/open_deep_research) | `1b7d2e80` | archived exemplar | GitHub marks the repository archived. It may inform an application-pattern wave but not the current framework cohort. |
| [microsoft/semantic-kernel](https://github.com/microsoft/semantic-kernel) | `a64827ec` | defer to lineage wave | It is active, but the first cohort already includes Microsoft's current Agent Framework and needs vendor and architecture diversity. A later migration study should compare the two directly. |

No candidate was excluded because of a negative quality judgment. These
decisions prevent duplicates, retired landing pages, and migration lineages
from inflating the cohort.

## Wave R2, 2026-08-27

**Mode:** popularity-directed, aspect-balanced expansion from 15 to 25
repositories.

**Discovery queries:** GitHub repository searches for agent frameworks,
multi-agent systems, agent memory, RAG, LLM evaluation, LLM observability, AI
workflows, and LLM guardrails. Candidates were compared using public repository
metadata, including star count, archive state, update time, and canonical owner.
Exact counts were recorded on the observation date and will drift.

**Selection rule:** inspect the most-starred candidates inside each aspect,
then retain one or more only when they add a distinct mechanism. Stars determine
discovery order, not inclusion by themselves. Product-line duplicates,
maintenance successors, archived projects, and broad platforms that add no new
mechanism remain in the screened-out table.

**Added:** Dify, Mem0, LlamaIndex, RAGFlow, GraphRAG, DSPy, Promptfoo, Phoenix,
NeMo Guardrails, and OpenHands. The additions cover visual workflow assembly,
memory, data context, context engines, graph retrieval, program optimization,
evaluation and red teaming, observability, programmable guardrails, and a
multi-backend agent control plane.

**Lifecycle exception:** GraphRAG is retained as a maintenance-mode research
implementation because its graph-context method, explicit research boundary,
and indexing-cost warning add evidence not represented by a second current
general agent framework.

### High-star candidates screened out in R2

| Candidate | Stars observed | Decision | Reason |
|---|---:|---|---|
| [n8n](https://github.com/n8n-io/n8n) | 202,623 | screened out | Broad automation platform. Dify supplies the direct visual agent-workflow layer, while OpenHands supplies the agent control-plane layer. |
| [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) | 186,935 | screened out | Broad agent platform overlaps the existing runtime and application categories without closing a higher-priority mechanism gap in this wave. |
| [Langflow](https://github.com/langflow-ai/langflow) | 153,741 | screened out | Visual agent-workflow surface overlaps Dify. Their observed star counts were effectively tied, so Dify was selected for the broader RAG, agent, model-management, and observability surface visible in its README. |
| [LangChain](https://github.com/langchain-ai/langchain) | 145,146 | ecosystem overlap | The cohort already includes LangGraph for durable orchestration and LlamaIndex for data context. The broader parent ecosystem would double-count mechanisms. |
| [LightRAG](https://github.com/HKUDS/LightRAG) | 39,234 | defer | RAGFlow, GraphRAG, and LlamaIndex cover context engine, graph research, and data-framework roles. LightRAG remains a candidate for a retrieval-specific wave. |
| [Agno](https://github.com/agno-agi/agno) | 41,945 | screened out | Current agent-platform functionality overlaps the existing runtime cohort. |
| [Semantic Kernel](https://github.com/microsoft/semantic-kernel) | 28,507 | lineage overlap | Microsoft Agent Framework is the current multi-agent target in this cohort. Compare the two in a dedicated migration study. |
| [DeepEval](https://github.com/confident-ai/deepeval) | 17,914 | defer | Promptfoo covers comparative testing and red teaming, while Phoenix covers traces, datasets, and experiments. |
| [Ragas](https://github.com/vibrantlabsai/ragas) | 15,503 | defer | Retrieval evaluation is important but already adjacent to Promptfoo, Phoenix, and the retrieval cohort. It belongs in a focused evaluation wave. |
| [Flowise](https://github.com/FlowiseAI/Flowise) | 55,399 | archived | GitHub marked the repository archived on the observation date. |

Screening out a popular repository is not a negative appraisal. It prevents
stars and overlapping product scope from inflating a mechanism count.

## Recheck triggers

Re-run identity and lifecycle checks when a project changes canonical owner,
enters maintenance mode, archives, points to a successor, changes license
boundaries, or releases a material architecture revision. Re-run mechanism
appraisal when a linked evidence path changes or when the next code-traced wave
selects the repository.

## Wave R3, 2026-08-27

**Mode:** popularity-directed, mechanism-family expansion from 25 to 100
repositories.

**Discovery aspects:** orchestration and control planes, multi-agent research,
memory and retrieval, evaluation and observability, guardrails and sandboxes,
interoperability and tools, and coding agents. Public GitHub repository pages
provided the canonical identity, exact default-branch commit, archive state,
and dated star observation. Each pinned README was screened against the same 11
dimensions and Method v2 claim register.

**Added:** 75 nonduplicate repositories. The wave adds model gateways,
execution sandboxes, human evidence production, coding-agent modes, temporal
memory, tool authentication, browser action layers, multi-agent simulation,
benchmark harnesses, red teams, and trace-linked evaluation. Four preserved
research implementations use the `research-artifact` lifecycle, and AutoGen is
retained as `maintenance` because its README points to Agent Framework.

**Saturation rule:** this wave completes the breadth map, not the evidence
program. Future additions must close a named mechanism gap. The default next
step is code tracing and bounded execution against a specific claim, baseline,
failure mode, and independent verifier.

### Candidates screened out in R3

| Candidate | Decision | Reason |
|---|---|---|
| [SWE-agent](https://github.com/SWE-agent/SWE-agent) | lineage | Its README says `mini-swe-agent` supersedes it. The successor is included. |
| [PyRIT](https://github.com/Azure/PyRIT) | archived | GitHub marks the repository archived. |
| [PromptBench](https://github.com/microsoftarchive/promptbench) | archived | The canonical repository redirects to an archived Microsoft Archive project. |
| [LLM Guard](https://github.com/protectai/llm-guard) | archived | GitHub marks the repository archived. |
| [Roo Code](https://github.com/RooCodeInc/Roo-Code) | archived | GitHub marks the redirected canonical repository archived. |
| [Activepieces](https://github.com/activepieces/activepieces) | mechanism overlap | n8n and Promptflow already cover broad workflow automation and flow evaluation in this wave. |
| [Chroma](https://github.com/chroma-core/chroma) | storage overlap | The wave retains memory and retrieval frameworks that expose change, evaluation, or workflow mechanisms beyond vector storage. |
| [Milvus](https://github.com/milvus-io/milvus) | storage overlap | The wave avoids counting multiple vector databases as distinct collaboration mechanisms. |
| [Qdrant](https://github.com/qdrant/qdrant) | storage overlap | The wave avoids counting multiple vector databases as distinct collaboration mechanisms. |
| [Weaviate](https://github.com/weaviate/weaviate) | storage overlap | The wave avoids counting multiple vector databases as distinct collaboration mechanisms. |
| [LanceDB](https://github.com/lancedb/lancedb) | storage overlap | The wave avoids counting multiple vector databases as distinct collaboration mechanisms. |
| [Argilla](https://github.com/argilla-io/argilla) | human-evidence overlap | Label Studio was retained as the higher-starred human labeling and review surface for this breadth pass. |

These exclusions are scope and deduplication decisions, not quality judgments.
