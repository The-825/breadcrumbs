# Search-miss ledger

**Assumes:** you have somewhere a lookup can fail, a doc corpus, a settled-facts store, a
knowledge search command. Nothing else. This is a text file and a habit.

A lookup that finds nothing is the highest-signal event your knowledge layer produces, and
by default it is the only one you throw away. The session works around the gap, the answer
gets re-derived, and the fact that anyone went looking leaves no trace. The next session
hits the same wall at the same cost.

One appended line makes the gap visible and, more importantly, already scoped: the entry
names where the answer should live, so filling it is a task rather than an investigation.

Why this is a ledger and not an issue: most misses are small, and a queue of small issues
gets triaged into oblivion. A miss that recurs is the signal, and recurrence is only
visible when misses accumulate in one place, cheaply, without anyone deciding each one is
worth filing.

## The line format

One JSON object per line, append-only, no comment lines. Never edit or delete a line: a
gap that gets filled simply stops recurring, and the record of it having been a gap is
worth keeping.

```
{"date": "<ISO date>", "surface": "<where the lookup ran>", "query": "<verbatim>", "where_searched": ["<source>", "..."], "what_was_missing": "<one sentence>", "suggested_home": "<repo path, or 'unknown'>"}
```

| Field | What goes in it |
|---|---|
| `date` | ISO date the miss happened |
| `surface` | Where the lookup ran: a command name, `session`, `agent:<name>`, a scheduled job |
| `query` | The search term or question, verbatim. Do not clean it up; the wording is evidence |
| `where_searched` | Every source consulted before giving up |
| `what_was_missing` | One sentence: what you expected to find and did not |
| `suggested_home` | The repo path where the answer should live once written, or `unknown` |

Three example lines:

```
{"date": "2026-03-04", "surface": "session", "query": "which env var controls the sync retry window", "where_searched": ["config module", "RUNBOOK.md", "conclusions store"], "what_was_missing": "The retry window is hardcoded in the sync client and documented nowhere.", "suggested_home": "docs/RUNBOOK.md"}
{"date": "2026-03-11", "surface": "agent:doc-sync", "query": "who approves a schema change", "where_searched": ["CLAUDE.md", "authority ledger"], "what_was_missing": "The authority ledger covers deploys and data deletes but has no grant covering schema changes.", "suggested_home": "AUTHORITY_LEDGER.jsonl"}
{"date": "2026-03-11", "surface": "knowledge-search", "query": "refund netting", "where_searched": ["conclusions store", "dashboards/"], "what_was_missing": "Expected a settled fact about refund netting; the fact exists but is keyed to a bare noun and never surfaces.", "suggested_home": "conclusions store, re-key to dashboards/revenue.sql"}
```

The third example is the useful shape to recognize. The miss was not a missing fact. It was
an unreachable one, which is the same experience from the searcher's side and a different
fix entirely. See [docs/memory-measurement.md](../../docs/memory-measurement.md).

## Writing to it

Append by hand or with a three-line helper. Whichever you choose, two rules hold.

**Validate before appending.** A malformed line in an append-only JSONL file is a
permanent wart, and it will be read by tooling later. Parse the object and check the
required fields before the write.

**Screen the query for anything that must not be committed.** The query is captured
verbatim, which is what makes it useful and also what makes it the one field that can leak.
If your repo is subject to a privacy floor, reject the append outright on the patterns that
floor cares about (an identifier-shaped number, a name field, a credential) rather than
trusting the writer to notice. See
[templates/hooks/outbound-pii-screen.md](../hooks/outbound-pii-screen.md).

## Working the ledger

The ledger is not a to-do list and should not be groomed like one. Read it on a cadence,
looking for two things:

1. **Recurrence.** The same query shape from different dates or different surfaces. That is
   a real gap with demonstrated demand, and it goes to the top.
2. **Clustering by `suggested_home`.** Several misses pointing at one file usually means
   that file exists and is incomplete, which is a cheaper fix than it looks.

A one-off miss with no recurrence is often correct to leave. Not every question deserves a
durable answer, and writing one for every miss is how a knowledge layer bloats into
something nobody reads. The ledger's value is that it lets you tell the difference instead
of guessing.
