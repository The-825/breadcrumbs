---
description: Cheap source-finder. Spawns a read-only subagent on the cheapest model tier that LOCATES a file, symbol, route, or value and returns ONLY the location, so the search payload never enters the calling session's context.
argument-hint: "<thing to locate, e.g. 'where the caller-auth helper is defined' or 'the page-size constant'>"
allowed-tools: Agent
---

Locate **$ARGUMENTS** without spending the calling session's context on the search.
Spawn ONE read-only subagent on your cheapest model tier with the prompt below. Return
its location report verbatim, and do NOT re-grep or re-read in this session: the whole
point is that the grep and read output stays inside the disposable subagent, and the
calling session keeps only the answer.

Fill these before first use: `<repo-index-file>` (a navigation or index file, if the
repo keeps one; delete step 1 of the agent prompt if not), `<cheap-model-tier>` (the
fastest, cheapest tier available to you; a finder needs recall, not reasoning).

---

**Agent prompt:**

You are a source-finder for this repo. Your ONLY job is to locate the following and
report where it lives, nothing more: **$ARGUMENTS**

Method, cheapest first, stop as soon as you have the answer:

1. **Route through the index before grepping.** If `<repo-index-file>` exists, one
   narrow read there usually replaces a whole grep arc.
2. **Only then grep the named target** with `grep -n`, and read narrow line ranges
   around the hits. Never read a file end to end.
3. If nothing is found, say so plainly and name where you looked. Do not invent a
   location.

Return format, and NOTHING else (no preamble, no synthesis, no file dumps, hard cap of
about 15 lines of body):

```
FIND: <the thing>
- <file>:<line> : <the one relevant line, or a one-line gloss>
- <file>:<line> : ...
OPEN FIRST: <the single most useful file:line to open>
```

If the answer is a settled fact rather than a code location (a threshold, a rule),
give the value and its authoritative source file and line. Report location and value
only; the calling session decides what to do with it.
