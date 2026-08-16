# Ecosystem scout

Every interesting tool, repo, or talk you evaluate ends one of two ways by
default: adopted on enthusiasm or dismissed on stack mismatch. Both waste the
evaluation. The tool you would never install often carries one concept worth
folding into your own system, and the tool that demos beautifully often
duplicates something you already run. These rules force the concepts out of
every resource before any fit judgment happens, and give each concept exactly
one of five honest outcomes. Paste them into your agent rules file, or run
them as a slash-command skill that writes a dated report per resource.

**What this assumes:** a repo with a rules file and some existing conventions
to cross-check against, and a place to persist short evaluation reports (a
`scouted/` directory works).

```markdown
## Ecosystem scout rules

1. Extraction runs BEFORE any fit judgment. List the concepts a resource
   contains (name, one line, what stack it targets) before deciding
   anything. The default posture is mining, not gatekeeping: assume every
   non-trivial resource carries at least one concept worth stating, and
   conclude "nothing transfers" only after listing what was considered.
2. Separate the artifact from the idea inside it. A wrong-language tool, a
   wrong-domain product, or a self-promo post can still carry a lifecycle,
   a placement rule, or a verification discipline that transfers. Stack
   mismatch disqualifies the artifact, never the concept, and forces a
   second look for a borrow.
3. Cross-check every concept against your own repo before judging it.
   Grep the rules file, the skills, the helpers. The most common honest
   outcome is "we already do this," and finding the evidence is the value.
4. Every concept gets exactly one disposition:
   - have: already done here, name the in-repo evidence. A have is also
     an engagement signal: you have lived detail to contribute back.
   - improve: we have this, theirs does one thing ours does not. Name
     the delta and the existing artifact it folds into. This is the
     disposition a bare have/skip split silently swallows.
   - borrow: we lack this and the tactical rule is worth pulling in.
     Name the landing file before closing the report.
   - adopt: install wholesale. Rare; only for drop-ins with tight fit.
   - skip: the CONCEPT does not transfer, and the report says why it
     fails conceptually. "Wrong stack" alone is never a skip reason.
5. A report whose table is all skips with no extracted concepts is a red
   flag on the report, not on the resource.
6. Tools that auto-generate or overwrite your curated docs are
   disqualified by default. The rules file, the ledgers, and the design
   docs are the most valuable durable artifacts in the repo; a tool whose
   first action is scan-and-overwrite fails before its output quality
   matters. Assume overwrite unless its docs promise otherwise.
7. Persist the report (dated, one file per resource) and keep a follow
   list: every source you borrowed from, with a one-line takeaway and a
   shipped/docketed/passed status. The list is what turns scattered
   evaluations into a maintained edge.
8. Never build a docketed borrow just to make the report look productive.
   A borrow with no trigger waits for its trigger.
```

## Why the five dispositions instead of yes/no

A binary adopt/reject loses the two outcomes that carry most of the real
value. "Improve" is where a mature system usually lands: you already run the
pattern, and the external version has one field, one check, or one lifecycle
stage yours lacks; a binary would round that to "have it, skip" and the delta
evaporates. And "have" is not a null result: it is the signal that you can
engage the source's community with lived detail rather than opinions, which
is worth more than most borrows.

## The failure this closes

Without rule 1, evaluation collapses into vibes at first glance: the shiny
multi-agent dashboard gets adopted while the boring lint script with one
genuinely new idea gets closed as a tab. Without rule 6, a doc-generating
tool gets a fair hearing it has not earned and overwrites the files your
whole operation boots from. Without rule 7, the tenth evaluation re-derives
the first nine.
