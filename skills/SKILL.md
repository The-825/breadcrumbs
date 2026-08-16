---
name: breadcrumbs
description: Paste-able rule sets for agent-assisted repos, ledger hygiene, retrieval exams, tiered merge gates, and the operating discipline behind them. Use when setting up or hardening an agent-operated repository.
---

# breadcrumbs

**Assumes:** you run a coding agent (Claude Code or equivalent) against a repo
that matters, with a rules file the agent loads each session.

This kit is a set of paste-able rule blocks, each born from a concrete failure
in a real production repo. A skill here is not executable code; it is a
numbered rule set you drop into your own agent rules file (CLAUDE.md or
equivalent) and enforce as-is. Each file opens by naming the failure the rules
prevent, then gives you the block to copy.

## The skills

| Skill | Failure it prevents |
|---|---|
| [agent-session-efficiency.md](agent-session-efficiency.md) | Sessions costing twice what they should on whole-file reads and echoed output |
| [data-truth-rules.md](data-truth-rules.md) | Confidently wrong numbers: blanks read as missing, forms trusted over behavior |
| [feature-flag-lifecycle.md](feature-flag-lifecycle.md) | Features reversible only by revert instead of by config |
| [regression-layering.md](regression-layering.md) | Regressions caught at an expensive layer when a cheap one existed |
| [forward-only-migrations.md](forward-only-migrations.md) | Schema rollbacks that lose data a process still depends on |
| [reuse-first.md](reuse-first.md) | New code written where an existing helper, dependency, or one-liner already served |
| [adoption-verifier.md](adoption-verifier.md) | A rules file whose claims about its own repo have silently rotted |
| [delivery-protocol.md](delivery-protocol.md) | Full-file re-prints, unverified code, and open-ended clarifying questions |
| [propose-confirm-execute.md](propose-confirm-execute.md) | Irreversible actions taken before the operator saw what would happen |
| [ecosystem-scout.md](ecosystem-scout.md) | External tools adopted on enthusiasm or dismissed on stack mismatch, with the transferable concept lost either way |

## How to adopt

1. Read the skill file; each states its own assumptions in its header.
2. Copy the fenced rule block into your agent rules file.
3. Run the [adoption verifier](adoption-verifier.md) after copying, so a
   missed placeholder edit surfaces now rather than the day it bites.

The wider kit around these skills (ledger tools, CI guards, the merge gate,
the memory desk) lives one level up; [llms.txt](../llms.txt) routes by
problem.
