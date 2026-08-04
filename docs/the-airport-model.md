# The airport model

> This essay is where the wayfinding idea grows up.

An airport is the friendliest large system most people ever operate without a manual. You
have never seen the whole building. You could not draw the terminal map from memory. And
yet you walk in cold, follow a handful of signs, and end up at the right gate. That works
because the airport does not try to explain itself. It signs the next decision, and only
the next one: check-in, then security, then your concourse, then your gate. Each sign
assumes you know nothing about the ten decisions after it, and it does not care. It gets
you to the next one.

A data platform a stranger can operate on day one works the same way. That is the whole
point of numbering your datasets by function instead of naming them after their history.
In the architecture this kit supports, the numbers are the signs: 0 for the rulebook, 1
for what just landed from a source, 2 for the record you own and stand behind, 3 for what
gets served to a screen. Whoever inherits the warehouse does not memorize it. They read
the number and know which decision they are standing at. The number is wayfinding, not
decoration.

## Why signage beats a map

A map describes the whole building. Signage names the next choice. Both get you there,
but they fail differently, and the failure is the point.

A map goes stale the moment the building changes. Add a terminal and every printed map is
wrong. Hand a new hire a document that describes your entire data estate and the same
thing happens: it is out of date before they finish reading it, and they cannot tell
which parts. Signage does not have that problem. Each sign owns one decision and the
neighbors right next to it. Move a gate and you change one sign, not the whole map. In a
repo, that sign is the wayfinding stamp at the top of a routed file: what this file is,
its nearest neighbors, the date it was last checked. A wrong turn self-corrects at the
next sign instead of sending you back to the information desk.

This is the same instinct as the three-hop routing in
[context-budget.md](context-budget.md): name the destination class, then the shelf, then
the file, each hop carrying next-hop signage only. Nobody loads the terminal map into
their head. They follow signs, cheaply, one decision at a time.

## The airport is more than its signs

Here is where the analogy earns its keep, and where it stops being about one warehouse.

Signage is what a traveler sees. It is not what makes an airport an airport. Underneath
the signs is a coordinated operation the traveler never watches: a control tower that
says who moves and when, security that decides who gets past the door and with what,
ground crews that turn a plane around on a schedule, gates assigned and reassigned all
day, a baggage system that routes ten thousand bags on one floor without a human tracking
any single one. The signs are the surface. The operation is the system.

A single well-numbered warehouse is the signage. A whole institution running on this
architecture is the airport: many sources feeding many terminals, a routing layer that
keeps them navigable, access gates that decide who reads and who writes, automated crews
that move data on a schedule and raise a hand when a run does not land, and a control
tower that refuses an action it cannot verify. One office can run on wayfinding alone. A
campus needs the operation.

## Reflection in code

The operation is not something you admire from the lounge. It is already in this repo, in
parts, and every part has a code shape.

- **The control tower** is the rules file every session boots from and the human gate on
  every merge. Nothing moves that the tower did not clear. See
  [rules-spine.md](rules-spine.md) and the greenlight lane in
  [staging-promotion.md](staging-promotion.md).
- **Security** is the authority model: who may do which of the four things to a record,
  and where, enforced instead of remembered. The gates get named out loud, never assumed.
- **The ground crew** is the automation: the syncs and watchers that move data on a
  schedule and alert a human when a run does not land on time.
- **Wayfinding** is the numbering and the three-hop catalog, so a stranger navigates on
  day one instead of interviewing whoever built it.
- **The flight log** is the decisions ledger and the CI guards: every ruling and every
  check written down, so a scramble is a rebase and not an excavation.
- **The baggage system** is agent memory: cross-session state routed, reconciled, and
  timed out the way an airline routes ten thousand bags, with claims matched against
  the manifest and an owner named on everything left on the carousel. That system got
  its own essay: [floating-memory.md](floating-memory.md).

Each of those is a file or a check you can copy from this repo today. The airport is not
a picture of the future. It is the current parts, seen as one system.

## Where this goes next

Book 1 hands you the wayfinding: number the datasets, sign the next decision, build one
warehouse a stranger can run. That is a single terminal. Book 2, *The Architect's
Operating Model*, is the airport: the operating model that coordinates many terminals into
one institution that still navigates on day one. If Book 1 is how you make a system
legible, Book 2 is how you make a legible system run at scale, tower and security and
crews and all, reflected in code the whole way down.

You do not need the second book to start. Number your datasets, hang your first signs, and
put a human at the one gate that matters. The airport begins as a single well-signed
terminal that someone other than you can walk through.
