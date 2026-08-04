---
description: Five-phase whole-codebase optimization review. Baseline, frontend, transport, backend runtime, then regression guards. Fan-out review agents, evidence-only findings.
argument-hint: "[optional focus, e.g. 'frontend only' or 'transport']"
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, Agent
---

Run the five-phase optimization review. Scope: $ARGUMENTS (default: the whole codebase). Findings must be CONCRETE and evidence-backed (file:line plus a quantified estimate); no style nitpicks, no invented issues. Work on a fresh `<branch-prefix>/perf-<slug>` branch off `origin/<main-branch>`. Report first, then fix only what the operator approves (or what is trivially safe and reversible). The command opens nothing and merges nothing; fixes ship through the normal `/ship` flow.

Fill these before first use: `<static-assets-dir>` (client JS/CSS/HTML), `<server-source-dir>` (routes and helpers), `<audits-dir>` (where dated review reports live), plus the branch and base placeholders above.

## Phase 1: Baseline (run yourself, cheap)

```
ls -la <static-assets-dir>/*.js <static-assets-dir>/*.css <static-assets-dir>/*.html   # asset weight
wc -l <static-assets-dir>/<main-client-file> <static-assets-dir>/<main-markup-file>
grep -rnE "Cache-Control|compress" <server-source-dir> | head -10                       # transport basics
ls .github/workflows/; ls <e2e-tests-dir> | wc -l                                       # guard inventory
```

Record the numbers. They are the baseline every finding is judged against, and the before/after for anything fixed. If a prior review report exists in `<audits-dir>`, diff against it instead of starting cold.

## Phase 2: Frontend client inspection (review agent)

One `general-purpose` agent over the client code: boot-sequence cost (count boot fetches, parse-time heavy work), DOM thrashing (un-debounced input handlers doing full-table rebuilds; if a debounce helper exists, check it is USED), repeated full-array scans per keystroke, listener and timer leaks in re-run render functions, resident dataset arrays held longer than needed, dead or retired code still shipped, duplicate utility implementations across files, render-blocking asset order, client-storage use in hot paths (quota and eviction behavior). Demand an "already good" list too, so existing good patterns do not get re-fixed.

## Phase 3: Network and data transport (review agent)

One agent over the server routes plus the client fetch layer: over-fetching (a `SELECT *` or full-object fetch on a wide record when the UI renders a handful of fields; column or field projection), redundant boot round trips (several endpoints counting the same collection), response cache headers (static assets must not ship uncacheable; check the after-request layer and static-file max-age), compression coverage (JSON and static), stale-while-revalidate coverage gaps on heavy views, payload shape (verbose keys multiplied by thousands of rows), polling timers. Quantify in bytes using live row or record counts where available.

## Phase 4: Backend runtime (review agent)

One agent over the server code: per-request query fanout (count query calls per hot route; sequential queries that could be one query or run in parallel), caching gaps (settings or flag lookups per call versus a short TTL; no server-side cache on expensive rarely-changing aggregates), query cost patterns (full scans on wide tables, request-time schema discovery), cold-start import weight, worker/thread shape versus the workload, blocking work in the request path (in-request file builds, inline sync phases), duplicate aggregate logic across endpoints (the drift class where two surfaces disagree on the same number because each computes it separately).

## Phase 5: Prevention and regression safety (synthesize yourself)

For every accepted finding, name the LOWEST layer that can catch its recurrence, and propose or add the guard:

- an asset-weight budget check in CI (fail if the main client bundle's compressed size jumps more than `<threshold>` percent),
- a per-endpoint query-count budget test (a unit test asserting the query-call count),
- a timing assertion on the boot path in the end-to-end suite,
- a lint for un-debounced input handlers on filter inputs,
- cost or bytes-billed logging on the query helper for telemetry.

Verify existing guards still pass (parse checks, lints, the unit suite) before finishing.

## Output contract

One report (chat, plus optionally `<audits-dir>/PERF_REVIEW_<date>.md`): baseline table, findings ranked by impact with file:line evidence and quantified estimates, the "already good" inventory, and a top-N recommendation list (recommendation-first, not an options menu). Fixes ship per the normal rules: infrastructure and feature work in separate PRs, feature-slugged branches, verify before push.
