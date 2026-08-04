# The context budget: price what every session auto-loads

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

An agent harness attaches your rules file to every session automatically. Claude Code loads CLAUDE.md at session start; session-start hooks inject more; tool schemas and command listings ride along. All of it sits in the context window for the life of the session, and in API terms it is re-sent with every request. That surface is not free documentation. It is a recurring tax on every turn of every session, and it grows one well-meaning paragraph at a time until sessions spend more of their window on boilerplate than on work.

The fix is to treat context like money: price it, budget it, and enforce the budget in CI so it cannot silently regrow.

## Two price classes

Every file in the repo falls into one of two classes, and the classes are priced differently:

- **Boot set.** Files the harness auto-loads or a hook auto-injects: the rules file, the session handoff file, the machine index, anything a hook prints at start. Their cost recurs on every turn of every session, so they carry hard line budgets.
- **Routed.** Everything else: reference docs, runbooks, catalogs, archives. A routed file costs only what a narrow read pulls in, only in the sessions that need it. Routed files are unbudgeted; the discipline for them is reachability (a session must be able to find the right thirty lines), not size.

The whole program is moving content from the first class to the second without losing the ability to find it. That takes two pieces: a budget with teeth, and a routing shape that makes the moved content cheap to reach.

## The budget manifest

Put the budgets in one table, in one file, and make a CI test parse that table as its single source. An illustrative shape (the numbers are placeholders; fill in your own measurements):

| File | Class | budget_lines | Notes |
|---|---|---:|---|
| `CLAUDE.md` | kernel | 500 | Binding rules only; everything else routes |
| `SESSION_STATE.md` | handoff | 300 | Rolling; refreshed on checkpoint |
| `INDEX.yaml` | router | 450 | The catalog; machine-first |
| `KNOWN_ISSUES.md` | ledger, active lane | 200 | Resolved entries move to the archive lane |

Three conventions make the table enforceable rather than decorative:

- **The guard test parses this table.** A plain unit test reads the manifest, runs `wc -l` on each file, and fails the build when any file exceeds its budget. Budget cells stay bare integers so the parse is trivial; commentary goes in the Notes column. Because the numbers live in exactly one place, nothing else in the repo restates them (one source of truth per fact).
- **Raising a budget is allowed, in the same PR, with a reason.** Over budget means cut or relocate content first. If the growth is deliberate, the PR raises the number in the manifest and says why in one line. The point is not a frozen ceiling; it is that growth becomes a visible, reviewed decision instead of a drift.
- **The budget is a ratchet.** When a restructure lands and a file shrinks, tighten its budget toward the new size in the same PR. Headroom you leave behind gets spent.

## The routing shape: kernel, catalog, stamp

A budget forces content out of the boot set. The routing shape is what keeps that content findable in a bounded number of cheap reads. Three hops, each carrying next-hop signage only, the way airport wayfinding names the next decision point rather than describing the whole building:

1. **The kernel.** The rules file shrinks to binding rules plus a destination map. It names the *class* of destination ("data reference lives on the reference shelf"), never the detail. Rules stay in full; reference detail leaves.
2. **The catalog.** A machine-first index file maps each destination to a concrete file and anchor: an id, a path, a one-line scope. A session that needs the detail resolves the class to a file here, in one short read of a small file.
3. **The wayfinding stamp.** Every routed doc opens with a four-line comment: its catalog id, its scope in one line, its nearest neighbors, and the date it was last verified. The stamp means a wrong hop self-corrects in one cheap read: a session that lands on the wrong file learns, from the first four lines, what the file actually covers and where the neighbors are, instead of scrolling the whole thing to find out.

That airport-wayfinding idea reaches past routing. The [airport model](the-airport-model.md) develops it into the full operating-model picture: one warehouse is a signed terminal, a whole institution is the airport.

The stamp also carries the freshness contract. A doc-sync pass refreshes the verified date when it confirms the path and scope still hold; a session bumps the date only when it actually re-checked the entry. Stale stamps surface as a list you can act on, instead of as silent rot.

> **One production repo's measured baseline.** Before the restructure, the always-loaded rules file ran 915 lines, roughly 22,000 tokens at the chars-over-four estimate, paid by every session on every turn. Two passes later it was a 476-line kernel, roughly 14,000 tokens, with the moved detail living in routed catalogs behind stamps. The full boot set (rules file, hook output, command listings, tool schemas) still totaled 35,000 to 38,000 tokens, and a typical directed-read session sat at 55,000 to 75,000 tokens before task work began. Those last two numbers are the reason the budget exists: the boot set was already the largest single line item in every session, and it was the one line item no task could opt out of.

## Append-only files get archive lanes

A line budget on an append-only ledger fights its purpose, so ledgers split into two lanes: a small curated lane that is budgeted and boot-injected, and an unbudgeted archive lane that never enters boot context and is reached by search. The relief valve is the move between lanes: when an issue resolves or a conclusion ages out of daily relevance, it moves to the archive, and the active lane stays under budget without deleting anything. [decision-capture.md](decision-capture.md) covers the ledgers themselves; the lane split is how they coexist with a budget.

## Cap the injection, not just the files

Session-start hooks that inject matched knowledge (settled conclusions for the files a branch touches, for example) need their own caps, or they become a second uncontrolled boot surface. Two limits work: a maximum number of entries per injected block, and a per-entry character truncation that ends with a pointer to the recall command for the full record. The session gets the scent; the full text stays one cheap lookup away.

## A router stub for other harnesses

If more than one agent tool works in the repo, each reads its own instructions file by convention, and duplicated instructions fork. Ship a stub instead: a file of a dozen lines that says "this repo's agent instructions live in the rules file; read it completely, then the handoff file, then the catalog" and explicitly forbids adding content to itself, because content there would drift from the source of truth. The stub costs nothing and closes off an entire class of divergence.

## The starter version

The full shape is a kernel, a catalog, stamps, a manifest, and a guard test. The afternoon version is three steps:

1. **Measure the always-loaded surface.** `wc -l` on the rules file and anything a hook injects. Most teams have never looked at this number; it is usually a surprise.
2. **Set one ceiling.** A single budget on the rules file, enforced by a five-line CI check. One number, one test.
3. **Move one section out.** Take the largest block of reference detail in the rules file, move it to its own doc, and leave a one-line pointer. You have a kernel and one routed file; the catalog and stamps can wait until there are enough routed files to need them.

The per-turn habits that control the *demand* side of the same budget (narrow reads, capped tool output, no re-reads) live in [skills/agent-session-efficiency.md](../skills/agent-session-efficiency.md). This doc is the supply side: what the repo itself forces every session to carry. The two meet in the middle, and both are enforceable today.
