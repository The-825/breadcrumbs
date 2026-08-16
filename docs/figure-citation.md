# Figure citation: numbers that cannot rot silently

> The enforcement half of "no unsourced numbers." A rule that every figure must
> trace to something real (this repo's own binding rule 3) is unenforceable by
> review alone: reviewers verify a number once, at merge time, and the number
> keeps being wrong ever after. Pairs with
> [artifact-correction-ledger.md](artifact-correction-ledger.md) (correcting a
> figure once, everywhere) and [context-budget.md](context-budget.md) (the same
> ratchet philosophy applied to size instead of truth).

**What this assumes:** a repo whose docs quote quantitative facts about the repo
or the system it runs (line counts, endpoint counts, live totals), a CI lane
that can run a script per PR, and a willingness to regenerate derived numbers
rather than hand-edit them.

## The problem

Prose quotes a number. The number was true the day it was written. The thing it
counts keeps changing, the sentence does not, and nothing in the pipeline knows
the two are connected. Six weeks later the doc says 47 views and the warehouse
has 63, and the reader has no way to tell a live figure from a fossil. Review
does not catch this class, because at review time the number IS right; it rots
after merge, in place, silently. The worst version is the number an agent then
reads back as ground truth and propagates into three more docs.

## The pattern

Two pieces, one for derived counts and one for quoted prose.

**1. A generated facts ledger.** Rot-prone mechanical counts (lines in the main
bundle, number of routes, number of views, number of tests) live in one
generated file, rebuilt deterministically from the tree by a script, marked
generated, never hand-edited. Idempotent: two runs on the same tree produce the
same bytes, so CI can fail on staleness by regenerating and diffing. Prose that
needs one of these numbers is told, in the rules file, to trust the generated
file over any hardcoded number it finds elsewhere.

**2. Inline citations on quoted figures, checked by CI.** Any prose sentence
that makes a live claim with a number cites the fact it quotes:

    The portal serves 47 reporting views [fact:reporting-views].

CI reads the last number before the tag and compares it against the ledger's
current value for that key. Match: fine. Mismatch: the PR fails with the exact
sentence and both values, so the fix is a one-line re-read, not an
archaeology dig. Commas and markdown emphasis in the quoted number are
tolerated; the key is what binds.

Two grammar rules carry most of the design's weight:

- **Point-in-time values must carry an as-of date in the key**
  (`[fact:active-flags@2026-08-13]`), because a value that mirrors a live store
  means nothing without its moment. When a newer snapshot lands, the citation
  fails until someone re-reads the figure and updates the sentence. That is the
  intended cost: the alternative is a sentence that silently becomes false.
- **Keys are permanent.** Rename a fact's label freely; never its key, or every
  citation to it breaks at once. Same contract as any public identifier.

## What it buys

- A wrong number fails a PR instead of misleading a reader. The check runs on
  every PR forever, which is the whole difference from review.
- Historical documents stay period-accurate for free: an uncited number is
  just prose, and only cited figures are asserted as live. The citation is an
  opt-in claim of currency, which makes "this was true then" and "this is true
  now" mechanically distinguishable at last.
- Agents inherit the discipline: a rules-file line saying "quote figures with
  their fact key, trust the generated ledger over prose" turns every future
  doc edit into a self-checking one.

## What it costs, honestly

Every genuinely live figure needs a key minted for it, and a fact nobody
bothered to add to the ledger cannot be cited, so coverage grows claim by
claim rather than arriving at once. Point-in-time citations fail on purpose
whenever their store moves, which is friction, and it is the friction working:
each failure is a sentence that would otherwise have gone quietly stale.
