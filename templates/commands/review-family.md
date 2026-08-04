---
description: Grouped operator review of a family of like surfaces - build a ledger of the whole family, walk it in numbered groups, every question ships a recommended pick, rulings captured verbatim same turn, completion gated on a roll-up showing every item dispositioned.
argument-hint: "<family, e.g. 'feature toggles', 'report definitions', 'form schemas'>"
allowed-tools: Bash, Grep, Read, Edit, Write
---

Run a grouped review of the **$ARGUMENTS** family with the operator. Use this when a
whole class of like surfaces (every toggle, every report, every integration mapping)
needs a human ruling per item and the items are too many for one sitting: the ledger
makes the review resumable, and the numbering makes the rulings capturable.

Fill these before first use: `<ledgers-dir>` (where review ledgers live, e.g. `docs/reviews/`),
`<conclusions-store>` (the settled-facts file, per `templates/CONCLUSIONS_TEMPLATE.md`).

## Step 1: create or locate the ledger

`<ledgers-dir>/<FAMILY>_REVIEW_LEDGER.md`. If new, seed it with a header (purpose,
protocol, status legend `pending / in review / reviewed / build items open / closed`),
an empty **build-item roll-up** section, and an **inventory table** listing every item
in the family in review order, with live usage counts and a status column. Enumerate
the inventory from reality (grep, config, the live system), never from memory; a review
that starts from a stale inventory rules on ghosts and misses the real stragglers.

## Step 2: build each group's dossier before presenting it

Walk the inventory in groups sized for one sitting. Before presenting a group, gather
its facts from live reality: each member's current value or shape, every downstream
consumer and exactly what it reads or edits, known issues that touch it, and any
doc-vs-live drift. The operator rules on evidence you assembled, not on questions you
are outsourcing.

## Step 3: numbered questions, each with a recommended pick

Every open decision in the group is a numbered question WITH a recommendation: one
pick and one line of why, not a menu of options. Keep the numbering stable within the
sitting so rulings can arrive as bare numbers.

## Step 4: the operator rules by number

Record each ruling VERBATIM in the ledger's section for that group (e.g. `ruling 4:
"approve"`). A ruling that arrives as an aside or a rider still gets numbered and
recorded. Never paraphrase a ruling into what you think it meant.

## Step 5: execute, tick, capture

Execute what the rulings unlock: small items same turn, larger items become build items
in the roll-up. Tick the inventory status. Capture every durable ruling to
`<conclusions-store>` THE SAME TURN it lands, keyed to the most relevant file and
tagged with the family name. A ruling that lives only in the sitting's transcript gets
re-litigated next session.

## Step 6: roll-up gate at close

The review is not closed when the last group is ruled. It closes when the build-item
roll-up shows every item dispositioned: grouped by gate (operator-gated / blocked on
upstream / implementation-ready), each pointing at its section, shipped items struck
through with their PR numbers cited. Then mark the ledger REVIEW COMPLETE with the
date. An undispositioned item is an open loop wearing a closed review's clothes.
