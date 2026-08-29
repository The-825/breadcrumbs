# Collaborative intelligence repository collection log

## 2026-08-29: public assessment transfer

**Mode:** deterministic public-only import into the existing repository
landscape.

The transfer contained 226 assessment sources representing 224 unique public
repositories. Two duplicates collapsed inside the transfer, ten repositories
matched the existing 100-record landscape, and 214 new identities entered the
ledger at the unscreened `source-assessment` evidence depth. The result at
transfer time was 314 unique assessed repositories. [Wave
R4](#wave-r4-2026-08-29), the same day, then triaged those 214 against the
landscape method's inclusion rule; the ledger holds 206 repositories today,
all at a reviewed evidence depth.

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

## Wave R4, 2026-08-29

**Mode:** triage of an already-imported, unfiltered list, not new discovery.

The 214 repositories imported by the [public assessment transfer](#2026-08-29-public-assessment-transfer) (`selection_aspect: "portfolio-memory-scout"`) were originally collected for an unrelated purpose (personal tool and idea scouting), not screened against this ledger's inclusion rule. D-45 (`planning/DECISIONS.md`) ruled they get triaged against the landscape method's real inclusion bar before any mechanism review: public, canonical, contains code or a specification relevant to at least one `CI-001` through `CI-017` claim, and pinnable to a reproducible revision.

**Included:** 106 repositories, each fetched live (README, stars, license, archive state, and a pinned 40-character commit SHA from its `/commits` page) and given the same 11-dimension mechanism review as Waves R1 through R3. Full table: [Wave R4 inventory](collaborative-intelligence-repository-landscape-wave-r4.md).

**Excluded:** 108 repositories, each screened out for a documented, factual, one-sentence reason (a curated list or curriculum, a repository with no visible collaboration-relevant mechanism, an inaccessible repository, or a duplicate of a repository a prior wave already screened out). None appear in the machine-readable register or the human-facing site, consistent with how Waves R1 through R3 treat a screened-out candidate.

**Cross-wave duplicate caught:** `milvus-io/milvus` was present in the transferred list and, on first pass, triaged in. It duplicates a candidate Wave R3 already screened out on 2026-08-27 for storage overlap ("the wave avoids counting multiple vector databases as distinct collaboration mechanisms"). The D-44 transfer's automated dedup only matches against repositories that already hold an `R-` id, so it could not catch an overlap with a name that was screened out and therefore never assigned one. Moved to excluded for consistency with the R3 precedent. A future transfer's dedup pass should check incoming identities against every screened-out candidate name across all collection-log waves, not only against assigned `R-` ids.

### Repositories screened out in Wave R4

| Repository | Reason |
|---|---|
| [1771-Technologies/lytenyte](https://github.com/1771-Technologies/lytenyte) | React data grid library; AI agent skills are an incidental developer-productivity feature, not a documented collaboration mechanism. |
| [actions/dependency-review-action](https://github.com/actions/dependency-review-action) | GitHub Action for dependency-vulnerability and license scanning in PRs; a static-analysis tool with no agent-collaboration mechanism. |
| [Agent-RL/ReCall](https://github.com/Agent-RL/ReCall) | Single-agent RL training framework for tool-use; documents benchmark evaluation but no human-AI or multi-agent collaboration mechanism. |
| [akullpp/awesome-java](https://github.com/akullpp/awesome-java) | Curated awesome-list of Java frameworks and libraries, not software with a collaboration mechanism. |
| [alexiocassanifm/anthropic-certifications](https://github.com/alexiocassanifm/anthropic-certifications) | A certification study kit/curriculum (wiki notes, practice questions) delivered via Claude Code skills, not a collaboration-mechanism implementation. |
| [AmrMKayid/friday](https://github.com/AmrMKayid/friday) | Zero-star, two-commit personal project with no accessible README content or documented mechanism. |
| [anthropics/claude-cookbooks](https://github.com/anthropics/claude-cookbooks) | Collection of illustrative Jupyter notebooks demonstrating Claude API usage patterns; not a single software system with its own collaboration mechanism. |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | A plugin marketplace/directory with submission and installation rules; the README does not itself document an agent-collaboration mechanism. |
| [anthropics/courses](https://github.com/anthropics/courses) | A curated set of educational courses on the Claude API, not software implementing a collaboration mechanism. |
| [anthropics/skills](https://github.com/anthropics/skills) | Single-agent instruction/skill library for Claude; README documents no collaboration topology, workflow state, memory, or authority mechanism beyond loading a skill into one agent's context. |
| [arkivanov/decompose](https://github.com/arkivanov/decompose) | Kotlin Multiplatform lifecycle/navigation library for app UI architecture, unrelated to agent collaboration. |
| [asgeirtj/system_prompts_leaks](https://github.com/asgeirtj/system_prompts_leaks) | A collection of leaked AI system prompts; a dataset archive, not software with a collaboration mechanism. |
| [avelino/awesome-go](https://github.com/avelino/awesome-go) | Curated awesome-list of Go libraries, not software. |
| [aws/serverless-application-model](https://github.com/aws/serverless-application-model) | Infrastructure-as-code CloudFormation macro for serverless resources; no agent-collaboration mechanism documented. |
| [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) | An output-formatting style skill for coding-agent responses; personal utility, no documented agent-collaboration mechanism. |
| [binhnguyennus/awesome-scalability](https://github.com/binhnguyennus/awesome-scalability) | A curated awesome-list of scalability resources and articles, not software. |
| [blakeblackshear/frigate](https://github.com/blakeblackshear/frigate) | NVR/object-detection software for IP cameras; no agent-collaboration mechanism documented. |
| [bradautomates/claude-video](https://github.com/bradautomates/claude-video) | Single-purpose Claude Skill that extracts video frames/transcripts for analysis; documents no human-authority, memory, or collaboration-topology mechanism, only a fixed ingestion pipeline. |
| [btw-so/open-source-alternatives](https://github.com/btw-so/open-source-alternatives) | A curated directory of open-source SaaS alternatives, not software with an agent-collaboration mechanism. |
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | Diagram-rendering skill/template pack for coding agents; documents visual output formatting only, no collaboration mechanism observed in the README. |
| [cdmorozov/claude-tutors](https://github.com/cdmorozov/claude-tutors) | Tutoring skills for Claude on math/programming subjects; no agent-collaboration mechanism documented. |
| [cloud-custodian/cloud-custodian](https://github.com/cloud-custodian/cloud-custodian) | Cloud governance/compliance rules engine for AWS/Azure/GCP; README documents no AI-agent collaboration mechanism. |
| [cncf/landscape](https://github.com/cncf/landscape) | Curated dataset/taxonomy powering the CNCF Cloud Native Landscape visualization, not agent-collaboration software. |
| [codecrafters-io/build-your-own-x](https://github.com/codecrafters-io/build-your-own-x) | A curated curriculum of tutorials for rebuilding technologies from scratch, not software. |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | Curated directory of 1000+ Claude skills/plugins with links to external implementations, not a single software system with its own mechanism. |
| [datakind/student-success-tool](https://github.com/datakind/student-success-tool) | Predictive-modeling tool for student-advising insights; documents human decision authority but no agent-collaboration mechanism. |
| [datopian/portal-apple](https://github.com/datopian/portal-apple) | A CKAN data-portal frontend template; unrelated to agent-collaboration mechanisms beyond an optional supplementary chat widget. |
| [dbeaver/dbeaver](https://github.com/dbeaver/dbeaver) | A universal database GUI client; its bolted-on AI chat feature is not a documented agent-collaboration mechanism. |
| [decalage2/awesome-security-hardening](https://github.com/decalage2/awesome-security-hardening) | A curated awesome-list of security hardening resources, not software. |
| [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) | Developer-preview agent harness whose README documents only a generic plugin/extension architecture and a compatibility-breaking-changes warning; no collaboration topology, authority, memory, or evaluation mechanism described in usable detail. |
| [devoteamgcloud/dataform-assertions](https://github.com/devoteamgcloud/dataform-assertions) | SQL-based data-quality assertion package for Dataform; no agent/AI collaboration mechanism documented. |
| [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) | A curated curriculum, not software. |
| [DovAmir/awesome-design-patterns](https://github.com/DovAmir/awesome-design-patterns) | Curated awesome-list of design-pattern resources, not software. |
| [easystats/report](https://github.com/easystats/report) | An R package for automated statistical reporting; unrelated to agent collaboration. |
| [EbookFoundation/free-programming-books](https://github.com/EbookFoundation/free-programming-books) | A curated list of freely available programming books and courses, not software. |
| [eriklindernoren/ML-From-Scratch](https://github.com/eriklindernoren/ML-From-Scratch) | Educational NumPy implementations of ML algorithms, not software addressing agent collaboration mechanisms. |
| [EtiennePasteur/jean-claude](https://github.com/EtiennePasteur/jean-claude) | HTTPS MITM proxy for stubbing/freezing Claude Code's own API responses; a single-tool debugging/config utility, not a collaboration mechanism. |
| [featbit/featbit](https://github.com/featbit/featbit) | Feature-flag management platform, does not document an agent-collaboration-specific mechanism. |
| [FlowiseAI/Flowise](https://github.com/FlowiseAI/Flowise) | Archived, no-code agent-workflow builder; the actual README documents no agent-collaboration mechanism at review depth, only install steps and a pointer to external docs. |
| [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) | A single CLAUDE.md prompting-guideline file shaping one coding agent's behavior; documents no collaboration topology, workflow state, authority, or memory mechanism. |
| [GokuMohandas/Made-With-ML](https://github.com/GokuMohandas/Made-With-ML) | Educational course/curriculum for building production ML systems, not an agent-collaboration mechanism. |
| [googleapis/genai-toolbox](https://github.com/googleapis/genai-toolbox) | An MCP server exposing database tools to agents/IDEs; documents interoperability and semantic versioning but no agent-collaboration mechanism (roles, memory, authority, or traces) at the coordination layer. |
| [GoogleCloudPlatform/cloud-data-quality](https://github.com/GoogleCloudPlatform/cloud-data-quality) | A BigQuery data-quality validation CLI; unrelated to agent collaboration mechanisms. |
| [GoogleCloudPlatform/generative-ai](https://github.com/GoogleCloudPlatform/generative-ai) | A curated collection of sample notebooks and tutorials for Google Cloud generative AI products; the README does not itself document a collaboration mechanism. |
| [GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog) | Minimal samples/toolbox repo for a GCP catalog product; README documents no collaboration mechanism at review depth. |
| [GoogleCloudPlatform/terraform-google-dataplex-auto-data-quality](https://github.com/GoogleCloudPlatform/terraform-google-dataplex-auto-data-quality) | Terraform module for deploying GCP Dataplex data-quality rules; infrastructure-as-code, unrelated to agent collaboration. |
| [Hack-with-Github/Awesome-Hacking](https://github.com/Hack-with-Github/Awesome-Hacking) | A curated collection of awesome lists, not software. |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | A curated awesome-list of Claude Code resources, not software. |
| [huggingface/transformers](https://github.com/huggingface/transformers) | General-purpose model-definition library for ML inference and training; README documents no agent-collaboration mechanism. |
| [immo2n/Friday-AI](https://github.com/immo2n/Friday-AI) | Thin personal hobby assistant project with no collaboration mechanism beyond basic SQLite caching. |
| [ismailsaoulaj/reddit-mcp-server](https://github.com/ismailsaoulaj/reddit-mcp-server) | A Reddit-access MCP tool server operating in request-response mode; the README explicitly states no multi-agent handoff or orchestration framework is supported. |
| [jamiepine/voicebox](https://github.com/jamiepine/voicebox) | A local voice-cloning/TTS studio with an MCP speak/transcribe tool add-on; the core product does not document an agent-collaboration mechanism beyond basic tool exposure. |
| [Jaspersoft/jasperreports](https://github.com/Jaspersoft/jasperreports) | Java reporting/PDF-generation library; no AI agent or human-AI collaboration mechanism documented. |
| [JCarterJohnson/vibecoded-design-tells](https://github.com/JCarterJohnson/vibecoded-design-tells) | A Reddit-derived dataset and analysis toolkit ranking AI-generated design tells; no documented agent-collaboration mechanism. |
| [jobsta/reportbro-lib](https://github.com/jobsta/reportbro-lib) | PDF/Excel report generation library, no agent-collaboration mechanism. |
| [Julian-Ivanov/jarvis-voice-assistant](https://github.com/Julian-Ivanov/jarvis-voice-assistant) | Single-agent voice assistant with a linear speech-to-action pipeline; no state, memory, evaluation, or authority-boundary mechanisms documented beyond direct voice-command control. |
| [kamranahmedse/developer-roadmap](https://github.com/kamranahmedse/developer-roadmap) | A curated collection of career/skill roadmaps and educational content, not software. |
| [kedacore/keda](https://github.com/kedacore/keda) | Kubernetes event-driven autoscaling infrastructure; unrelated to agent collaboration. |
| [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) | Agent-skill library teaching a single agent to read/write Obsidian file formats (Markdown, Bases, JSON Canvas); no collaboration topology, workflow state, or authority mechanism documented. |
| [kilimchoi/engineering-blogs](https://github.com/kilimchoi/engineering-blogs) | A curated list of engineering blogs, not software. |
| [KristenZHANG/TriggerBench-Official](https://github.com/KristenZHANG/TriggerBench-Official) | Placeholder repository stating code and dataset will be released soon; nothing reviewable exists yet. |
| [makenotion/notion-mcp-server](https://github.com/makenotion/notion-mcp-server) | Stateless single-tool MCP wrapper around the Notion API; no collaboration topology, workflow state, or authority boundary beyond generic read-only token scoping. |
| [microsoft/presidio](https://github.com/microsoft/presidio) | General-purpose PII detection/anonymization library, not framed around or documenting an AI agent/human-AI collaboration mechanism. |
| [milvus-io/milvus](https://github.com/milvus-io/milvus) | Already screened out in Wave R3 as storage overlap (2026-08-27): the wave avoids counting multiple vector databases as distinct collaboration mechanisms. Wave R4's independent triage initially included it before this precedent was checked; removed for consistency. |
| [mohammedayanrafiq/FRIDAY](https://github.com/mohammedayanrafiq/FRIDAY) | Conceptual voice-assistant placeholder with implementation restricted to private access; no documented collaboration mechanism. |
| [mono424/punktraster](https://github.com/mono424/punktraster) | Personal utility (a canvas loading-animation library) unrelated to agent collaboration. |
| [Neeeophytee/agent-stylebooks](https://github.com/Neeeophytee/agent-stylebooks) | Portable writing-style guide skills for AI agents; no agent-collaboration mechanism documented. |
| [netlify-templates/astro-platform-starter](https://github.com/netlify-templates/astro-platform-starter) | Netlify/Astro web starter template, unrelated to agent collaboration. |
| [obra/superpowers-skills](https://github.com/obra/superpowers-skills) | Archived skills library auto-cloned by a Claude Code plugin; README documents no agent-collaboration mechanism. |
| [ollama/ollama](https://github.com/ollama/ollama) | Local LLM inference runtime; README documents model serving and ecosystem integrations, not an agent-collaboration mechanism. |
| [ossf/scorecard](https://github.com/ossf/scorecard) | Automated OSS security-posture scorer; does not document an agent-collaboration mechanism. |
| [ossu/computer-science](https://github.com/ossu/computer-science) | A self-directed computer science degree curriculum, not software. |
| [papers-we-love/papers-we-love](https://github.com/papers-we-love/papers-we-love) | A curated list of computer science papers for reading groups, not software. |
| [pentaho/pentaho-reporting](https://github.com/pentaho/pentaho-reporting) | Java business-intelligence reporting engine, unrelated to AI or agent collaboration. |
| [philterd/phileas](https://github.com/philterd/phileas) | A general-purpose Java PII/PHI redaction engine with no documented AI-agent collaboration mechanism. |
| [PiLastDigit/Code-With-Claude](https://github.com/PiLastDigit/Code-With-Claude) | Conference transcript archive, not software with an agent-collaboration mechanism. |
| [practical-tutorials/project-based-learning](https://github.com/practical-tutorials/project-based-learning) | A curated list of project-based tutorials, not software. |
| [public-apis/public-apis](https://github.com/public-apis/public-apis) | A curated list of free public APIs, not software. |
| [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch) | Code companion to a book on building LLMs from scratch; an educational curriculum, not a collaboration-mechanism implementation. |
| [redis/redis](https://github.com/redis/redis) | General-purpose in-memory database, does not document an agent-collaboration-specific mechanism. |
| [rhysd/actionlint](https://github.com/rhysd/actionlint) | A static syntax/security checker for GitHub Actions workflow files; no agent-collaboration mechanism documented. |
| [ripienaar/free-for-dev](https://github.com/ripienaar/free-for-dev) | A curated list of free-tier cloud/SaaS/PaaS/IaaS offerings, not software. |
| [RohanAdwankar/ws-term](https://github.com/RohanAdwankar/ws-term) | WebSocket terminal-tunneling utility for restricted VMs; no agent/AI collaboration mechanism documented. |
| [SAGAR-TAMANG/friday-tony-stark-demo](https://github.com/SAGAR-TAMANG/friday-tony-stark-demo) | A personal voice-assistant demo with basic MCP tool-calling; no documented workflow state, human-authority, or memory mechanism beyond function calling. |
| [sdmg15/Best-websites-a-programmer-should-visit](https://github.com/sdmg15/Best-websites-a-programmer-should-visit) | Curated list of external links for programmers; archived by its owner, not software. |
| [shadcn-ui/ui](https://github.com/shadcn-ui/ui) | A UI component library; unrelated to agent collaboration. |
| [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) | A curated documentation/knowledge-base repository aggregating Claude Code practices from other projects, not software implementing a collaboration mechanism itself. |
| [sindresorhus/awesome](https://github.com/sindresorhus/awesome) | The master curated index of awesome-lists, not software. |
| [SohailKhan0525/skills](https://github.com/SohailKhan0525/skills) | Personal skill library; documents only basic skill routing, too thin to inform any listed claim. |
| [sqlfluff/sqlfluff](https://github.com/sqlfluff/sqlfluff) | SQL linter/auto-formatter; no agent-collaboration mechanism documented. |
| [sruthik27/creating-claude-md](https://github.com/sruthik27/creating-claude-md) | A skill that generates CLAUDE.md documentation files; does not document an agent-collaboration mechanism. |
| [stanford-earth/stanford_r25](https://github.com/stanford-earth/stanford_r25) | Drupal module integrating with a room-reservation system; unrelated to agent/AI collaboration. |
| [step-security/harden-runner](https://github.com/step-security/harden-runner) | General GitHub Actions runner security/EDR tool (network egress, file-integrity, process monitoring); not specific to AI agent or human-AI collaboration. |
| [sukeesh/jarvis](https://github.com/sukeesh/jarvis) | CLI personal-assistant plugin framework; no state, memory, evaluation, or authority-boundary mechanisms documented beyond direct user commands. |
| [supabase/supabase](https://github.com/supabase/supabase) | A Postgres backend-as-a-service platform (auth, REST/GraphQL, realtime, storage); no agent-collaboration mechanism documented. |
| [teng-lin/notebooklm-py](https://github.com/teng-lin/notebooklm-py) | Unofficial Python/CLI wrapper exposing NotebookLM's web features to agents via undocumented APIs; documents no collaboration topology, authority, or verification mechanism of its own. |
| [thomaspoignant/go-feature-flag](https://github.com/thomaspoignant/go-feature-flag) | Feature-flag management system for software rollout control; not an agent-collaboration mechanism. |
| [tiimgreen/github-cheat-sheet](https://github.com/tiimgreen/github-cheat-sheet) | A Git/GitHub tips and features cheat sheet, not software. |
| [tl-its-umich-edu/my-learning-analytics](https://github.com/tl-its-umich-edu/my-learning-analytics) | Student-facing learning-analytics dashboard for Canvas LMS; no AI agent or collaboration mechanism described. |
| [trimstray/the-book-of-secret-knowledge](https://github.com/trimstray/the-book-of-secret-knowledge) | Curated collection of cheatsheets, manuals, and tool links, not software. |
| [uber/piranha](https://github.com/uber/piranha) | Deterministic AST-based static-analysis tool for removing stale feature-flag code; no AI/LLM or agent-collaboration mechanism. |
| [UniTime/unitime](https://github.com/UniTime/unitime) | A traditional academic scheduling/timetabling system with no AI-agent involvement. |
| [Unleash/unleash](https://github.com/Unleash/unleash) | Feature-flag management platform, does not document an agent-collaboration-specific mechanism. |
| [ussumant/useful-agent-skills](https://github.com/ussumant/useful-agent-skills) | Single published skill (quota-based model switching); too thin to document a broader collaboration mechanism. |
| [Valera-Studio/Valera-Studio-Harness](https://github.com/Valera-Studio/Valera-Studio-Harness) | not accessible (GitHub returns 404 on both the repo page and a retry) |
| [vinta/awesome-python](https://github.com/vinta/awesome-python) | Curated awesome-list of Python libraries and tools, not software. |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | A curated awesome-list of 1000+ agent skills, explicitly a hand-picked compilation rather than software. |
| [zizmorcore/zizmor](https://github.com/zizmorcore/zizmor) | General GitHub Actions/CI security static-analysis linter, explicitly not specific to AI agent workflows. |

These exclusions are relevance and deduplication decisions, not quality judgments.
