---
description: Recall earlier context from this session's own transcript, or any prior session's, without re-deriving it - grep the local transcript files (plus compaction saves) and return timestamped excerpts.
argument-hint: "<query> [--all]"
allowed-tools: Bash, Grep, Read
---

Recall **$ARGUMENTS** from the local session transcripts. Use this BEFORE re-deriving
anything that was already discussed, decided, or measured earlier in this session or a
prior one: one grep is cheaper than one re-derivation, and much cheaper than a wrong
guess.

Fill these before first use: `<transcripts-dir>` (where your harness stores session
transcripts on disk; Claude Code keeps per-project JSONL transcripts under
`~/.claude/projects/<project-slug>/`), `<compaction-saves-dir>` (where pre-compaction
snapshots land, if you keep them via a pre-compact hook; skip if you do not).

## Run

Grep the CURRENT session's transcript plus its compaction saves for the query, and
print each hit as a timestamped excerpt with a couple of lines of surrounding turn
context. With `--all`, sweep every transcript for this project, newest first: that is
the post-rotation move, where a fresh session references its predecessor's full
conversation on demand instead of carrying it. Keep limits deliberately tight (a
handful of matches, a small context window per match) and widen only on a miss.

## When to reach for it

- Mid-session: "what exactly did the operator say about X", "which figure did we
  verify", "what was that error string" - anything from before the current context
  window's horizon.
- After compaction: the summary says something happened but the detail is gone.
  Recall the detail instead of trusting the summary; compaction summaries are lossy
  by design.
- After a session rotation: the predecessor's decisions are one `--all` query away,
  covering whatever the durable notes did not fold in.

## Floors

- Matches print in-session only. Never copy sensitive data from recall output into
  memory files, commits, PR bodies, or anything else that leaves the machine.
- Recall is evidence of what was SAID, not what is TRUE now: re-verify any live
  figure against its canonical source before restating it.
- Durable knowledge still routes to its durable home: a ruling found via recall that
  is missing from the conclusions store gets captured there the same turn.
