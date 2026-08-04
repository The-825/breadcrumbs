---
description: What do we know about this path, file, or area? Grep the conclusions store, recent git history, and the repo index in one shot, instead of re-deriving from source.
argument-hint: "<path or feature name>"
allowed-tools: Bash, Grep, Read
---

Answer "what do we know about **$ARGUMENTS**?" by pulling from the durable-knowledge layer. Do NOT re-read the code file first; this command surfaces what has already been learned, not a fresh derivation from source.

Fill these before first use: `<conclusions-store>` (the repo's CONCLUSIONS.jsonl, the settled-facts file defined by the conclusions-store template, `templates/CONCLUSIONS_TEMPLATE.md` in the companion repo), `<repo-index-file>` (a navigation or index file, if the repo keeps one), `<design-docs-dir>` (per-feature design docs, if any).

Run these lookups (batch in parallel where possible):

1. **Conclusions matches:** grep the conclusions store for the term, both as an exact path key and as a substring:
   `grep -F '$ARGUMENTS' <conclusions-store> 2>/dev/null | head -30`
   If the repo also keeps a bulk-mined archive file alongside the curated core, grep it second and label those hits `(archive)` in the synthesis; curated outranks archive on any conflict. Tag any conclusion older than about 6 months with an `(aging, re-verify)` cue so a stale settled fact is not trusted blindly.

2. **Index pointers:** `grep -inE '$ARGUMENTS' <repo-index-file> | head -15` (skip if the repo has no index file).

3. **Recent commits touching it:**
   `git log --oneline --all --since="6 months ago" -- '*$ARGUMENTS*' 2>/dev/null | head -10`
   Fallback if that returns nothing: `git log --oneline --all --since="6 months ago" --grep="$ARGUMENTS" | head -10`

4. **Design doc if any:** `ls <design-docs-dir> 2>/dev/null | grep -i "$ARGUMENTS" | head -5`

Then produce a concise synthesis (target 30 lines or fewer):

```
# WARP: $ARGUMENTS

## Settled conclusions
- <date> <what> (<evidence>)
- ...

## Where it lives (index)
<the routing pointers, one per line>

## Recent activity (git)
- <sha> <subject>
- ...

## Related docs
- <design-docs-dir>/<X>.md, one-line gloss if the filename is opaque
```

If a section is empty, print `_(none)_` under its header; do not omit the header. The shape stays stable so the operator's eye finds sections fast.

End with one line: **"Recommend reading: <path>"**. Pick the single most useful file to open first based on what came back: the design doc if present, else the newest conclusion's evidence pointer, else the file itself.

Do NOT open or dump the code file. The point of this command is to LOCATE fast; the operator opens what they need after.
