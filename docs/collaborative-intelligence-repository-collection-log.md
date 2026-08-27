# Collaborative intelligence repository collection log

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

## Recheck triggers

Re-run identity and lifecycle checks when a project changes canonical owner,
enters maintenance mode, archives, points to a successor, changes license
boundaries, or releases a material architecture revision. Re-run mechanism
appraisal when a linked evidence path changes or when the next code-traced wave
selects the repository.
