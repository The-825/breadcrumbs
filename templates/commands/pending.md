---
description: Sweep the repo for every idea, follow-up, or "next step" that was raised and never landed, and report each with its CURRENT status so it can be reintroduced or retired.
argument-hint: "[optional theme filter]"
allowed-tools: Agent
---

Spawn ONE `general-purpose` subagent with the prompt below (insert the theme argument if given). Return its full report. This command reads and reports only; it edits nothing.

Edit the sweep list in the prompt to match your repo layout before first use.

---

**Agent prompt:**

You are the idea tracker for this repository. The standing problem: ideas get raised mid-build ("What's NOT in scope", "Next steps", "future work", "wishlist", "watch item", "on request"), then the session moves on and they are never reintroduced. Your job is to harvest ALL of them and report each with its **current contextual status**, because an idea deferred months ago may have been quietly delivered since, or invalidated by a later decision. Theme filter (optional): **$ARGUMENTS**

**Where deferred ideas live (sweep all; adjust paths to this repo):**

1. `<changelog-file>`: "not in scope" and deferred lines inside entries
2. `<roadmap-file>` (and any secondary backlog file): pending items and wishlists
3. The rules file (CLAUDE.md or equivalent): the known-issues ledger (active entries carry actions) and any "later" notes
4. `<audits-dir>`: audits and post-mortems end with recommendations; most were never all actioned
5. `<design-docs-dir>`: designs awaiting review or partially shipped
6. PR bodies if reachable: the "What's NOT in scope" sections of recent PRs
7. Grep sweeps: `grep -rn "TODO\|FIXME\|next PR\|follow-up\|future work\|wishlist\|on request\|deferred\|Phase 2\|watch item" --include="*.md" --include="*.py" --include="*.js"` (dedupe; ignore vendored code and node_modules)

**For EACH harvested item, determine current status by checking the live repo state** (grep for the artifact it proposed; check the changelog for a later entry that delivered it):

- **DELIVERED**: it shipped after being deferred (cite where). Propose removing the stale mention.
- **STILL OPEN, RIPE**: its prerequisite has since landed; it could start now (say what unblocked it).
- **STILL OPEN, BLOCKED**: name the concrete blocker (data not collected, awaiting an operator decision, an external system).
- **INVALIDATED**: a later decision or finding made it moot (cite). Propose retiring it.
- **RECURRING-DATE**: periodic re-runs (an annual refresh, a start-of-cycle check). List with the next due window.

**Deliverable:** a single register, grouped by status, each row `idea | first raised (file:line) | current status + evidence | recommended action (reintroduce now / schedule / retire)`. Lead with the top 5 RIPE items (highest value, now unblocked). Keep it at or under 600 words. Cite file:line for every claim or mark it "unverified". Do NOT edit files; report only.
