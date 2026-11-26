# Pointers and trails

> This essay is where the routing idea grows up. It separates two kinds of cue a system
> can leave: pointers that say where to go next, and trails that say what already
> happened. A repo needs both and should keep them apart.

A large system is easiest to operate when it does not try to explain itself all at once.
It tells you the next decision, and only the next one: this file, then its neighbors,
then the shelf they sit on. Each pointer assumes you know nothing about the ten decisions
after it, and it does not care. It gets you to the next one.

A data platform a stranger can operate on day one works the same way. That is the whole
point of numbering your datasets by function instead of naming them after their history.
In the architecture this kit supports, the numbers are the pointers: 0 for the rulebook,
1 for what just landed from a source, 2 for the record you own and stand behind, 3 for
what gets served to a screen. Whoever inherits the warehouse does not memorize it. They
read the number and know which decision they are standing at. The number is routing, not
decoration.

## Why pointers beat a map

A map describes the whole system. A pointer names the next choice. Both get you there,
but they fail differently, and the failure is the point.

A map goes stale the moment the system changes. Add a dataset and every copy of the
diagram is wrong. Hand a new hire a document that describes your entire data estate and
the same thing happens: it is out of date before they finish reading it, and they cannot
tell which parts. A pointer does not have that problem. Each one owns one decision and
the neighbors right next to it. Move a file and you change one pointer, not the whole
map. In a repo, that pointer is the routing stamp at the top of a routed file: what this
file is, its nearest neighbors, the date it was last checked. A wrong turn self-corrects
at the next pointer instead of sending you back to the person who built it.

This is the same instinct as the three-hop routing in
[context-budget.md](context-budget.md): name the destination class, then the shelf, then
the file, each hop carrying only the pointer to the next. Nobody loads the whole map into
their head. They follow pointers, cheaply, one decision at a time.

## Pointers face forward; this repo is named for the other half

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

A pointer only ever answers "where do I go from here." It has no memory of where you
have already been, and it does not need one: the reader behind you gets the identical
pointer, whether this is their first visit or their hundredth. That is exactly right for
routing, and exactly wrong for the other half of what an agent session needs, which is
not where to go next but what already happened here.

That other half is what gives this repo its name. A trail is not a pointer. It is a
trace left by someone who already walked the path, readable by whoever comes after: this
is where I went, this is what I found, this is what I got wrong and corrected. Pointers
are stateless and forward-only, the same for every reader. Trails are stateful and
backward-facing, specific to what actually happened. A system needs both and keeps them
separate on purpose, because a routing pointer that also tries to tell you which earlier
change was reverted stops being a pointer. So does this repo: the routing stamps and the
three-hop catalog are the pointers, and the decisions ledger, the append-only
supersession record, and the settled-facts store in
[ledger-tools](../templates/ledger-tools/README.md) are the trail. A session that only
has pointers can find the file; a session that also has the trail knows why the last
session went a different way, and does not have to learn it the hard way twice.

## The new hire's first weeks

The pointers and the trail meet in one figure: the newcomer. Watch what actually happens
to someone new in their first weeks on a team, because it is the same thing that happens
to a memory system.

In the first week, the newcomer takes in everything, because they cannot yet tell what
matters. Which meetings run long, which dashboard is trusted, the odd naming convention
in one folder, which build is always red. All of it lands. That is not a failure of
attention, it is the correct opening move when you do not yet know the terrain: capture
first, judge later. This kit's journal works the same way. `mem add` is deliberately
cheap and unfiltered for exactly this reason: the capture step must never be where
judgment happens, because at capture time you do not yet have the experience to judge
with.

Discernment comes on the second pass, not the first. A few weeks in, the newcomer's
memory quietly sorts the haul: the naming convention was worth keeping, the red build
turns out to be a known flake worth one line in the notes, the long meeting was noise.
Store, reference, skip. In this kit that sorting is a mechanical step, not a hope: the
gardener's promotion pass reads the raw journal and decides row by row what graduates
into the index, what gets flagged for a human call, and what stays behind. The filter is
separate from the capture, and it runs later, with more context than the moment of
capture had.

And by the third month the system shows its value. The newcomer walks in and the work is
familiar, not because they memorized a map but because their own past left cues along
the path: that error message means the cache is stale, that folder means the legacy
export. The notes they made earlier now fire on contact with the work itself. That is
what a lookup hit is, a cue left by a previous session firing for the current one. And
the sharpening never stops: cues that keep proving useful stay fresh, cues that stop
being checked go stale on a horizon that adapts to how fast the ledger actually moves.
The newcomer does not just accumulate, they consolidate, and so does the desk.

The arc, first-week sweep to sorted notes to felt familiarity, is the whole memory
lifecycle of this kit in one figure: capture everything (journal), discern later
(gardener), retrieve on return (index lookup), and let disuse fade what stopped
mattering (the staleness horizon). A system that skips the first stage never captures the
cue it later needs; a system that skips the discernment stage drowns in its own first
week forever. It takes both, in that order, every time the terrain is new.

## Pointers are not the whole system

Here is where the idea stops being about one warehouse.

A pointer is what a reader sees. It is not what makes a system work. Underneath the
pointers is a coordinated operation the reader never watches: a rules file that says who
moves and when, an authority model that decides who gets past the door and with what,
automation that runs on a schedule, a catalog that keeps everything navigable, and
checks that refuse what cannot be verified. The pointers are the surface. The operation
is the system.

A single well-numbered warehouse is the pointers. A whole institution running on this
architecture is the operation: many sources feeding many consumers, a routing layer that
keeps them navigable, access rules that decide who reads and who writes, automated jobs
that move data on a schedule and raise a hand when a run does not land, and a gate that
refuses an action it cannot verify. One office can run on pointers alone. A campus needs
the operation.

## Reflection in code

The operation is not something to admire from a distance. It is already in this repo, in
parts, and every part has a code shape.

- **The gate** is the rules file every session boots from and the human approval on every
  merge. Nothing moves that the gate did not clear. See [rules-spine.md](rules-spine.md)
  and the greenlight lane in [staging-promotion.md](staging-promotion.md).
- **Authority** is the model for who may do which of the four things to a record, and
  where, enforced instead of remembered. The boundaries get named out loud, never
  assumed.
- **Automation** is the syncs and watchers that move data on a schedule and alert a human
  when a run does not land on time.
- **Routing** is the numbering and the three-hop catalog, so a stranger navigates on day
  one instead of interviewing whoever built it. This is the pointer half.
- **The record of what happened** is the decisions ledger and the CI guards: every ruling
  and every check written down, so a scramble is a rebase and not an excavation. This,
  with agent memory below, is the trail half: not where to go, but what already happened
  here.
- **Agent memory** is cross-session state routed, reconciled, and timed out, with claims
  matched against the record and an owner named on everything left unclaimed. That system
  got its own essay: [floating-memory.md](floating-memory.md).

Each of those is a file or a check you can copy from this repo today. None of it is a
picture of the future. It is the current parts, seen as one system.

## Where this goes next

Everything above is a single warehouse: numbered and routed well enough that a stranger
can run it. The harder version is a whole institution, many systems coordinated into one
that a newcomer can still navigate on day one, gate and authority and automation and all,
reflected in code the whole way down. That is the problem I am working on now, and the
longer story of how I got here is *From Archivist to Architect*.

You do not need any of that to start. Number your datasets, add your first pointers, and
put a human at the one gate that matters. The institution begins as a single well-routed
warehouse that someone other than you can walk through.
