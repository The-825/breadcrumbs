---
description: Autonomous scout discovery. Generates candidate tools/repos/concepts from the live ecosystem (no URL given), dedupes against prior scout reports, deep-evaluates the top few with the /scout rubric, and ships dated reports plus a ranked digest.
argument-hint: "[optional focus topic]"
allowed-tools: WebSearch, WebFetch, Read, Grep, Glob, Write, Bash
---

Run an autonomous discovery pass for the scout system. The binding blocks in your shared agent preamble apply (see `templates/AGENT_PREAMBLE_TEMPLATE.md` in the companion repo, or your repo's installed copy).

Fill these before first use: `<scout-reports-dir>` (the dated-reports directory `/scout` writes to, e.g. `docs/scouted/`), `<branch-prefix>`, `<your-stack>` (the languages and platforms your repo actually runs), `<roadmap-file>`, `<conclusions-store>`, and the rotating lanes in step 2.

**The lane split:** `/scout <url>` (this command's required companion, in this same command set) evaluates a specific external resource the operator hands it. `/scout-discover` finds the subjects worth scouting in the first place: it browses the ecosystem, generates candidates, dedupes against everything already in `<scout-reports-dir>`, and runs the /scout evaluation on the top few. No URL required. Do not blur that split.

## Procedure

### 1. Load the dedupe set

List `<scout-reports-dir>` and read its `DISCOVERY_DIGEST.md` if present. Every existing report filename is a prior subject. A subject already scouted is NEVER re-evaluated, whatever its verdict. One exception: the resource itself materially changed (their v2 shipped) AND the prior report is over 90 days old; then add a NEW dated report per the folder's additive-only rule, marked as a re-scout. Dedupe applies to the SUBJECT (the specific repo or tool), not the topic space: one memory tool being scouted does not retire the memory lane. Sweep-style reports evaluate several subjects in one file, so also grep report bodies for each candidate's name before treating it as new.

### 2. Generate candidates (cap 30)

Search 4 to 6 lanes per run: ALWAYS the two standing lanes, plus 2 or 3 rotating lanes (pick the least-recently-run, per the digest's run headers). If a focus argument was given, it replaces the rotating lanes; the standing lanes still run.

**Standing lanes (every run):**
- **Agent memory:** persistent memory systems and patterns for LLM agents, knowledge distillation into durable docs, memory-layer tooling, agent knowledge bases.
- **Workflow and orchestration:** multi-agent orchestration patterns, CI and automation ergonomics, merge queues and review automation, operator-productivity routines.

**Rotating lanes (fill in for your repo; 4 to 8 is plenty):** one lane per live concern, e.g. your agent harness's ecosystem (commands, hooks, subagent patterns), your primary stack's operations (cost guards, linting, schema drift), your product surface's UX patterns, compliance-safe analytics for your regulated data class, ingestion and webhook reliability, doc automation (docs-from-diffs, changelog agents, knowledge-base sync).

**Sources per run** (hard bound: 15 web fetches total):
- WebSearch, 2 or 3 queries per lane; include the current year in at least one query per lane.
- GitHub trending once per run (https://github.com/trending?since=weekly, plus a filter for your primary language).
- One awesome-list delta or Hacker News sweep (hn.algolia.com) when a lane suggests it.
- Any directory site specific to a lane (e.g. an MCP or plugin directory): mine its latest/official feeds and lane-targeted searches only, never category crawls; the long tail is clone-heavy.

Record reached/skipped status per source for the digest header; if a source is unreachable after 2 tries, mark it skipped and move on. Each candidate: name, URL, one line on what it is, which lane surfaced it.

### 3. Score and cut

Drop dedupe hits first. Score the rest 0 to 10 across: stack fit (`<your-stack>`; tooling written for a stack you do not run caps at borrow-parts), problem fit (a live theme in `<roadmap-file>`, your known-issues ledger, or recent `<conclusions-store>` entries), signal (recency, momentum, substance over marketing), adoptability (license, size, curated-doc safety). Keep the top 5 at most, all scoring 6 or higher. If fewer than 2 clear the bar, STOP: no reports, no PR. Print the lanes and queries tried plus the near-misses, and end.

### 4. Deep-evaluate the survivors (cap 5)

For each survivor run the full `/scout` evaluation per `scout.md`; that file is the single source for the rubric and report format, do not restate it here. Write the standard report to `<scout-reports-dir>/<slug>-YYYY-MM-DD.md` with one provenance line added directly under `Source:`:

    Discovered: /scout-discover YYYY-MM-DD, <lane> lane

All of scout.md's report discipline applies: wrong-stack artifacts are borrow-at-most, auto-generators that overwrite curated docs are disqualified, thin resources are called thin.

### 5. Update the digest

`<scout-reports-dir>/DISCOVERY_DIGEST.md`, newest run on top, directly under the file header. Run block format:

    ## Run YYYY-MM-DD
    Lanes: <lanes> | Sources reached: <list> | Skipped: <list, why>
    Considered: N candidates, D dropped as dupes, K evaluated

    | Rank | Subject | Verdict | Why it matters here | Report |
    |---|---|---|---|---|
    | 1 | <name> | borrow-parts | <one line> | [<slug>-<date>.md](<slug>-<date>.md) |

    Skips: <name> (<one-line reason>); <name> (<reason>)
    Near-misses: <optional: candidates scoring 5, or strong-but-wrong-stack; one line each. Future runs read these when picking rotating lanes>

Keep the 12 most recent run blocks; drop older blocks (their reports stay in the folder).

### 6. Ship

In-session: commit on `<branch-prefix>/scout-discover-<YYYY-MM-DD>` and open a `docs:` PR (reports plus digest only), ready for review, never draft. Opening the PR is where this command stops: it never merges, never enables auto-merge, and never applies an approval label. If a scheduled workflow owns commit, branch, and PR mechanics in your repo, leave the edits uncommitted and exit; the workflow picks them up.

## Guardrails

- Read-only research. Never install, clone-and-run, or adopt code during a discovery run; adoption is a separate, human-approved build PR.
- Diffs touch ONLY `<scout-reports-dir>`.
- No PII, no secrets, no model identifiers, no em-dashes in anything newly written. Avoid pasting long numeric IDs or email addresses from external content.
- Cost caps are hard: 30 candidates scored, 5 evaluated, 15 web fetches.
- Never rewrite an existing report or a prior digest run block (additive-only, same as the folder rule).
