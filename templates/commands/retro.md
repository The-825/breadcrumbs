---
description: Post-task retrospective - mine the arc that just finished for lessons and land every lesson as exactly one artifact (a conclusions append, a command/skill edit, or a roadmap wishlist row). Evidence in, artifact out; nothing stays only in chat.
argument-hint: "[PR number | branch] (default: the arc just finished in this session)"
allowed-tools: Bash, Grep, Read, Glob, Edit, Write
---

Run a retrospective over **$ARGUMENTS** (default: the arc just finished in
this session).

Fill these before first use: `<conclusions-store>` (your conclusions ledger,
see the CONCLUSIONS template), `<roadmap-wishlist>` (wherever deferred work
rows live, e.g. planning/ROADMAP.md), and, if you keep them, the optional
exhaust logs in Step 1.

The operating principle: refinement runs on EVIDENCE (misses, denials,
failures, repeated friction), not on periodic rewrites of things that work.
A retro with no findings changes nothing and says exactly that; that is a
valid result, not a failure to produce.

## Step 1: gather the evidence

Cheap reads only; the retro must cost less than the lessons are worth.

- The arc itself: the PR diff and body, plus the conversation's own friction
  points (wrong first hops, re-reads, denied tool calls, retried commands,
  mid-arc corrections from the operator).
- Optional exhaust, if your repo keeps it: a search-miss log (lookups that
  found nothing and got re-derived by hand), a flake ledger (rows the arc
  added or reopened), a command-use log (friction or fail outcomes noted
  during the arc). Missing logs are fine; the arc alone is enough evidence
  to start.

## Step 2: classify each lesson into exactly one bin

1. **Re-derived what should have been known** (a routing bug). The fact
   existed or was derivable, and the session paid to re-derive it. Land it
   as a `<conclusions-store>` append in your house format. When the failure
   was "the right doc was never reached", fix the pointer where lookups
   start (the rules file, an index, a read-first note) instead; that is the
   routing-side form of the same fix.
2. **Repeated friction** (the same manual dance twice or more). Candidate
   command or skill edit. If the edit is small (a step, a flag, a pointer),
   make it now on the current feature branch. If it needs its own design,
   file a wishlist row instead; never leave a half-written command.
3. **A procedure worth encoding** (the arc invented something reusable). A
   `<roadmap-wishlist>` row in its existing format, or a new command once
   the procedure has run twice; the second run is the promotion bar, the
   first is a sample size of one.

Each lesson lands as EXACTLY ONE artifact: conclusions append, command
edit, or wishlist row. No double-filing, and no "noted for later" without
an artifact. Rulings the operator issued mid-arc should already be captured
by the same-turn rule; the retro verifies they were, it does not substitute
for it.

## Step 3: land and report

Apply the artifacts (same branch or PR when small; wishlist rows
otherwise). Then report one table and stop:

| lesson | evidence | bin | artifact |

Two sentences max after the table. A zero-lesson retro reports "no
findings, nothing changed" in one line, which is the loop working, not
failing.
