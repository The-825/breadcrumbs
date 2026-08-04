---
description: Evaluate an external URL (repo, product page, article) for relevance to this codebase and produce a written scout report with a have / borrow / adopt / skip verdict per concept.
argument-hint: "<url>"
allowed-tools: WebFetch, Bash, Grep, Read
---

Scout the external resource at **$ARGUMENTS** for relevance to this repo. Produce a report the operator can skim in under two minutes, then persist it to `<scout-reports-dir>` (a dated-reports directory, e.g. `docs/scouted/`).

Steps (batch where possible):

1. **Fetch** the URL via WebFetch. Use a targeted prompt asking for: what the thing IS, what problem it solves, tech stack, what artifacts it ships (library / prompts / product / paper), and any explicit mention of agents, LLM tooling, testing, or memory.

2. **Extract concepts** the resource contains. For each: name, one-line description, what stack it targets.

3. **Cross-check each concept against this repo.** For each concept, run one or two of:
   - Grep the rules file (CLAUDE.md or equivalent) and any repo index file for related terms.
   - Grep the conclusions store (`<conclusions-store>`, the CONCLUSIONS.jsonl file if you keep one) for a prior conclusion on the concept.
   - Look at `.claude/commands/` for a command that already covers it.
   - Search the codebase for a matching helper or convention.

   Assign each concept one of four dispositions:
   - **`have`**: already done here in some form (name the repo evidence).
   - **`borrow`**: not present, but the tactical rule is worth pulling into an existing command or rules-file rule (name where it would land).
   - **`adopt`**: worth installing or copying wholesale (rare; only when the artifact is a drop-in and the fit is tight).
   - **`skip`**: wrong stack, wrong domain, or not applicable to how this repo works (name the reason).

4. **Score fit + write the report** at `<scout-reports-dir>/<slug>-YYYY-MM-DD.md`:

```
# Scout: <name of the external thing>
Source: <url>
Fetched: <date>
Verdict: adopt / borrow-parts / skip

## What it is
<1-2 sentences>

## Fit dimensions
- Stack fit: <yes/no + why>
- Domain fit: <yes/no + why>
- Novel value beyond the current repo: <yes/no>

## Concept-by-concept

| Concept | Disposition | Notes |
|---|---|---|
| <name> | have | <repo evidence> |
| <name> | borrow | <tactical rule to lift + target file> |
| <name> | skip | <why> |

## Recommendation
<one paragraph. What to do (nothing / add a specific rule to a specific file /
open a PR on a named theme). If nothing, say nothing plainly.>

## Follow-up (if any)
- Conclusions-store candidate entry (optional): { "path": "process", "when": "<date>",
  "what": "Reviewed <thing>: <one-sentence takeaway>", "evidence": "<report path>" }
- PRs to open (if any).
```

5. **Print** the verdict plus a one-line summary in the chat so the operator sees the decision without opening the file, then point at the persisted report path.

Report discipline:

- Do not recommend adopting artifacts written for a different stack as code; at most `borrow` the concept. Name your stack in this rule when you install the command.
- Do not recommend adding a new command or rule that duplicates one this repo already has; name the existing one instead.
- If the resource is thin (a marketing page with no substance), say so plainly and skip the concept table.
- **Auto-generators that overwrite curated repo docs are disqualified by default** (`skip`). The tool must prove it PRESERVES human-authored content before its output quality even matters. Your rules file, index files, conclusions store, design docs, and session handoff file are the most valuable durable artifacts in the repo; a tool whose first action is to scan-and-overwrite them fails the fit test regardless of downstream capability. If a tool can be scoped to write only to a new path, never touching existing docs, that changes the analysis; assume overwrite unless its docs explicitly promise otherwise.

If the operator asks to skip persistence ("just tell me"), print the concept table in-conversation and stop; do not write the file.
