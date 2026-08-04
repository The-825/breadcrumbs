# The coordinator/seat model

> Companion to the multi-agent-hygiene doc in `docs/`: hygiene keeps agents from
> trampling each other's files, this pattern keeps a standing team of them coherent
> over weeks, not just one PR.

## The problem

One agent session per task works until you have five, ten, a dozen running against the
same repo across a week. Nobody can hold all of them in their head. Sessions duplicate
work because they can't see each other. Someone has to decide who does what next, and
if that decision only lives in your head, you're now the bottleneck every session waits
on.

## The pattern

Stand up one **coordinator** session that stays warm across the work, and a roster of
**seats**, lettered or named, that spin up cold and re-adopt their identity from a
charter file on every wake. The coordinator delegates; it doesn't do the work itself.

- **A durable seat map.** One file lists every seat, what it owns, and its current
  status. A seat that goes cold and comes back reads this file first and knows exactly
  who it is and what it was mid-task on, without you re-explaining.
- **Delegation flows down, status flows up.** The coordinator writes directives a seat
  reads on wake. A seat writes its own status back to its own file. Neither writes into
  the other's lane, so two sessions never fight over the same write.
- **A named coordinator, not an implicit one.** Someone (or some session) is
  explicitly the one who reads the whole roster and decides what's next. Without that
  role named, "who's doing what" degrades into whoever happens to be in the chat.
- **Seats are cheap to spin down.** Because identity lives in the charter file, not in
  session memory, a seat that goes idle for a week costs nothing and comes back exactly
  where it left off.

## When to use it

Worth the overhead once you're running enough concurrent agent work that you personally
can't hold the roster in your head, roughly three or more sessions with distinct,
ongoing responsibilities. Below that, a shared `SESSION_STATE.md` and normal PR review
is enough; don't build a seat map for one or two agents.

## What it isn't

Not a replacement for the merge gate or the decisions ledger. The coordinator model
solves "who is doing what right now"; it says nothing about "was this change safe to
merge" or "will this ruling survive next week." Pair it with the automerge gate
(`ci-kit/workflows/`) and the decision ledger (`templates/DECISIONS_TEMPLATE.md`).
