---
description: Review the current change set with a model-tier ladder. A cheap draft pass finds candidate defects, a stronger pass adversarially verifies each, and a whole-change reconcile pass runs only when the change is wide.
argument-hint: "[base ref or explicit paths, default origin/<main-branch>]"
allowed-tools: Bash, Agent
---

Review **$ARGUMENTS** (default: everything changed against `origin/<main-branch>`) with the tiered ladder: a draft tier reports candidate findings per file group, a verify tier adversarially rules on each, and a reconcile tier reads the whole change set only when it is wide enough to need one. The session stays on its own model; the tiers apply to the spawned subagents via the Agent tool's model override.

Fill these before first use: `<draft-model>` (cheap, e.g. your fast tier), `<verify-model>` (stronger, e.g. your deep tier), `<reconcile-model>` (whatever you trust with cross-file synthesis; the deep tier again is fine), `<wide-change-threshold>` (file count that triggers the reconcile pass; 6 is a good default).

## 1. Resolve the change set

- Empty `$ARGUMENTS`: run `git fetch origin <main-branch>`, then `git diff --name-only --diff-filter=ACMR origin/<main-branch>...HEAD`. If the branch has no upstream comparison, fall back to `git status -s`.
- `$ARGUMENTS` looks like a git ref (branch, tag, sha): diff against that ref instead.
- `$ARGUMENTS` is one or more explicit paths: review exactly those.
- If the resolved set is empty, say so and stop. Do not review nothing.

## 2. Run the ladder

1. **Draft.** Spawn `general-purpose` subagents with the model override set to `<draft-model>`, one per coherent file group (group by area: frontend files together, server routes together, SQL or schema files together, docs together). Each agent reads its files plus enough surrounding context to judge them, and reports every candidate finding as `file:line, failure scenario, confidence, severity`. Instruct them to report everything and not self-filter; filtering is the next pass's job.
2. **Break.** Spawn ONE `general-purpose` subagent with the model override set to `<verify-model>`. It takes the full draft-finding list and adversarially refutes each against the actual code: real defect or noise. It returns a real / not-real verdict per finding with a code-grounded reason. A finding it cannot rule on stays `unverified`.
3. **Reconcile (conditional).** Only if the change spans `<wide-change-threshold>`+ files, or the operator forces it: spawn one subagent with the model override set to `<reconcile-model>` that holds the whole change set and checks cross-file consistency and completeness (does every surface that cites the changed fact still agree; is anything the change implies missing). Otherwise skip it and say why: the reconcile pass is the expensive one and narrow changes do not need it.

If your harness has a deterministic review pipeline of its own, prefer it over ad-hoc orchestration and use this file as the explicit opt-in that calls it; the ladder above is the portable fallback that works in any session with an Agent tool.

## 3. Relay the result, plainly

- Confirmed findings first, most severe first, each as `file:line, one-sentence failure scenario`. If nothing was confirmed, say `tiered-review: no confirmed findings`.
- If any findings are unverified, list them under a clear "unverified (the verify pass did not rule)" heading so they are not mistaken for confirmed bugs.
- If any files were not reviewed (a dead subagent, a scoping cap), say plainly which. Do not present a partial review as complete.
- If the change-set discovery itself failed, say so and stop. Do NOT report a clean review over a failed discovery.
- Close with a 2 to 3 sentence reconcile summary when that pass ran; when it was skipped, one line saying the change was too narrow to warrant it.
- Do not paraphrase, re-derive, or second-guess findings beyond what the ladder returned.
