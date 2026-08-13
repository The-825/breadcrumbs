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

## Signs point forward; this repo is named for the other half

The phrase comes from a fairy tale before it comes from software. Hansel and Gretel
dropped crumbs through the forest so they could find their way home, and the crumbs
failed for one specific reason: birds ate them, and the trail vanished with nothing
durable behind it. That is the detail worth keeping. A trail only works if something
durable is doing the leaving, which is the whole design argument for the rest of this
essay.

Even inside the story there is a second answer, easy to miss. Once enough crumbs draw
enough birds, the birds themselves become visible from a distance, a flock moving
through one part of the forest and not another. A search party who never sees a single
crumb can still read that pattern and go the right direction. The signal survived the
trail's failure by leaving a trace one level up. That is not a design to build on, you
should never plan a memory system around hoping its failure gets noticed by somebody
else, but it points at the real fix: leave more than one kind of marker, in more than
one durable form, the way an actual trail through real woods gets marked. Not just
crumbs, but blazes cut into bark, cairns stacked from stone, broken branches turned to
point a direction, none of which a bird can eat and none of which depends on the others
surviving.

The fable maps onto the actual engineering problem closer than it first looks. An agent
session that forgets everything between visits is not missing a map, it is standing
where the crumbs used to be, the exact failure this repo exists to stop. A crumb that
survives but misleads is its own failure mode, maybe worse than none at all: a stale
fact sends the next session down the wrong path with full confidence, the same as a
hunter following a trail that has since moved. That is why a marker here always carries
a way to check itself, when it was left and whether anything since has superseded it,
not just that it exists. And more than one search party can enter the same forest
looking for the same thing, each unaware the other is already out there, duplicating
the walk and the risk, the same as two agent sessions doing the same undocumented work
at the same time. The fix for that is not faster searching. It is a trail both parties
can actually read, and a way for either one to see that someone is already on it (see
[multi-agent-hygiene.md](multi-agent-hygiene.md) and
[issue-backed-task-bus.md](issue-backed-task-bus.md)).

A sign only ever answers "where do I go from here." It has no memory of where you have
already been, and it does not need one: the traveler behind you gets the identical
sign, whether this is their first trip through the terminal or their hundredth. That is
exactly right for wayfinding, and exactly wrong for the other half of what an agent
session needs, which is not where to go next but what already happened here.

That other half is what gives this repo its name. A breadcrumb trail is not a sign. It
is a trace left by someone who already walked the path, readable by whoever comes
after: this is where I went, this is what I found, this is what I got wrong and
corrected. Signage is stateless and forward-only, the same for every traveler.
Breadcrumbs are stateful and backward-facing, specific to what actually happened. An
airport needs both and keeps them separate on purpose, a gate sign does not also try to
tell you which earlier flight got cancelled. So does this repo: the wayfinding stamps
and the three-hop catalog are the signage, and the decisions ledger, the append-only
supersession record, and the settled-facts store in
[ledger-tools](../templates/ledger-tools/README.md) are the crumbs. A session that
only has signage can find the gate; a session that also has the crumbs knows why the
last session went a different way, and does not have to learn it the hard way twice.

## The inexperienced traveler

The signage and the crumbs meet in one figure: the first-time traveler. Watch
what actually happens to someone new in a terminal, because it is the same thing
that happens to a memory system, and to a new hire in their first week.

On the first trip through, the traveler takes in everything, because they cannot
yet tell what matters. The gate numbers, the coffee smell near security, the odd
echo by baggage claim, which escalator was broken. All of it lands. That is not
a failure of attention, it is the correct opening move when you do not yet know
the terrain: capture first, judge later. A new staff member's first week works
the same way, and so does this kit's journal. `mem add` is deliberately cheap
and unfiltered for exactly this reason: the capture step must never be where
judgment happens, because at capture time you do not yet have the experience to
judge with.

Discernment comes on the second pass, not the first. Back home, or on the next
trip, the traveler's memory quietly sorts the haul: the gate-numbering scheme
was worth keeping, the coffee smell turns out to be a landmark ("security is
past the coffee"), the broken escalator was noise. Store, reference, skip. In
this kit that sorting is a mechanical step, not a hope: the gardener's
promotion pass reads the raw journal and decides row by row what graduates into
the index, what gets flagged for a human call, and what stays behind. The
filter is separate from the capture, and it runs later, with more context than
the moment of capture had.

And the third trip is where the system shows its value. The traveler walks in
and the terminal is familiar, not because they memorized a map but because
their own past left cues along the path: that smell means security is close,
that echo means baggage claim. The crumbs their memory dropped on earlier trips
now fire on contact with the place itself. That is what a lookup hit is, a cue
left by a previous session firing for the current one. And the sharpening never
stops: cues that keep proving useful stay fresh, cues that stop being checked
go stale on a horizon that adapts to how fast the ledger actually moves, the
way an unused landmark fades. The traveler does not just accumulate, they
consolidate, and so does the desk.

The arc, novice sweep to sorted landmarks to felt familiarity, is the whole
memory lifecycle of this kit in one figure: capture everything (journal),
discern later (gardener), retrieve on return (index lookup), and let disuse
fade what stopped mattering (the staleness horizon). A system that skips the
novice stage never captures the cue it later needs; a system that skips the
discernment stage drowns in its own first trip forever. It takes both, in that
order, every time the terrain is new.

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
  day one instead of interviewing whoever built it. This is the signage half.
- **The flight log** is the decisions ledger and the CI guards: every ruling and every
  check written down, so a scramble is a rebase and not an excavation. This, with the
  baggage system below, is the breadcrumb half: not where to go, but what already
  happened here.
- **The baggage system** is agent memory: cross-session state routed, reconciled, and
  timed out the way an airline routes ten thousand bags, with claims matched against
  the manifest and an owner named on everything left on the carousel. That system got
  its own essay: [floating-memory.md](floating-memory.md).

Each of those is a file or a check you can copy from this repo today. The airport is not
a picture of the future. It is the current parts, seen as one system.

## Where this goes next

Everything above is a single terminal: one warehouse, numbered and signed well enough that
a stranger can run it. The harder version is the whole airport, many terminals coordinated
into one institution that a newcomer can still navigate on day one, tower and security and
crews and all, reflected in code the whole way down. That is the problem I am working on
now, and the longer story of how I got here is *From Archivist to Architect*.

You do not need any of that to start. Number your datasets, hang your first signs, and
put a human at the one gate that matters. The airport begins as a single well-signed
terminal that someone other than you can walk through.
