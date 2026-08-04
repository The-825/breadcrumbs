---
description: Spawn a subagent whose only job is to refute the current diff. Surface real findings, dismiss noise. /ship runs this before pushing.
argument-hint: "[optional diff scope, defaults to origin/<main-branch>...HEAD]"
allowed-tools: Bash, Grep, Read, Agent
---

Adversarially verify the current change: spawn a subagent whose ONLY job is to argue the diff is wrong, then triage what comes back. Ship-time pass by default; also invocable standalone any time.

Two invocation modes:

- **From `/ship` (ship-time bar):** surface only high-confidence findings. Anything low-confidence gets logged as "adversarial noise, dismissed" and the flow continues. The bar is: would you actually block a push over this?
- **Standalone (`/adversarial-verify`):** lower the bar. Surface everything and let the operator triage. Useful as a second opinion on a diff before committing, or on a merged PR after the fact.

Steps:

1. **Scope the diff.** First refresh the base: `git fetch origin <main-branch>` so the merge-base is current (a cached remote ref goes stale fast on an active repo). Then `git diff origin/<main-branch>...HEAD --stat` names the affected files. If `$ARGUMENTS` is a path or pattern, scope to it. If the diff is empty, say so and stop. Print the branch name and `git log --oneline origin/<main-branch>..HEAD | head -3` up top so the operator sees what is being verified.

2. **Spawn the adversarial subagent** using the Agent tool (`general-purpose` subagent type). Prompt verbatim (do not soften):

   > You are reviewing a code change that is about to be pushed. Your ONLY job is to try to argue this change is wrong. Do not summarize the change. Do not add caveats about how it is "well-intentioned" or "reasonable."
   >
   > Read the diff first: `git diff origin/<main-branch>...HEAD`. Then read any file the diff modifies as needed for context. For each concern you find, output one entry in this structured shape (and NO other prose):
   >
   > ```
   > SEVERITY: high | medium | low
   > CONFIDENCE: high | medium | low
   > CONCERN: <one sentence stating what is wrong>
   > SCENARIO: <a concrete input, state, or sequence where this manifests as a bug or regression>
   > FIX: <one sentence on the specific change needed, or "unclear, needs investigation">
   > ---
   > ```
   >
   > Look specifically for: missing edge cases; silent failures introduced (a try/catch that swallows without logging, a promise without a catch, a fetch without a fallback state); assumptions that do not hold in production (field semantics where a blank means "No" rather than "missing"); regressions in adjacent code; insufficient tests for the added behavior; off-by-one errors; race conditions; ordering assumptions in tests; PII or real-looking IDs in fixtures; hidden coupling between files that changed and files that did not; wrong abstractions; hardcoded numbers that belong in the config registry; and any deviation from the standing rules in this repo's rules file (CLAUDE.md or equivalent).
   >
   > For each modified function or route: grep the repo for callers and check whether the change breaks any of them. For each modified test: consider what production regression the test now fails to catch.
   >
   > If you find zero real concerns, output the single word `NOTHING`. Do NOT invent concerns to seem thorough. Small mechanical changes (typo fixes, doc adds, single-line refactors) legitimately have nothing to refute.

3. **Triage the returned findings** with the operator:
   - **High severity + high confidence:** STOP. Print the finding, propose the FIX inline, and wait for direction. Do NOT let `/ship` proceed to push until resolved.
   - **Medium severity, or high severity with low or medium confidence:** print the finding and ask the operator quickly: fix inline / dismiss with reason / defer to a follow-up issue. In ship-time mode, a dismissal and its reason get recorded in the PR body (see the `/ship` template).
   - **Low severity + low or medium confidence:** in ship-time mode, log inline as `adversarial noise, dismissed: <one-sentence why>` and continue. Standalone, surface it for operator triage.

4. **Record the outcome** as a one-line summary:

   ```
   adversarial verify: N concerns raised (H high-conf, M needs-eye, L noise). K fixed inline, D dismissed, F deferred to #NNN.
   ```

   Print this before the push completes so the operator sees the pass ran and what it found. If `NOTHING` came back, print `adversarial verify: no concerns raised.` and let the flow continue.

## Design notes (not part of the output)

- The prompt is blunt on purpose. Review subagents tend to endorse the diff they were handed; instructing them to refute it, and banning hedge language, counters that tendency.
- The structured shape forces a split between severity and confidence. A `[low, low]` entry gets dismissed as noise, and that is correct behavior: a subagent that invents low-confidence concerns to seem thorough is the noise source this bar filters.
- Cost: one Agent call per invocation, typically 5-20k tokens depending on diff size. It pays for itself if it catches one real regression per ten ships; in the system this was extracted from, the pass caught a real name-resolution bug on its first run.
