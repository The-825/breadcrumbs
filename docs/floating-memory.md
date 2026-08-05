# Floating memory: the airport model applied to agent memory

> Grows out of [the-airport-model.md](the-airport-model.md): that essay makes a
> system legible to a stranger; this one makes a fleet of agent sessions legible to each
> other. Pairs with [multi-agent-hygiene.md](multi-agent-hygiene.md) and
> [decision-capture.md](decision-capture.md).

An agent session is a traveler with no memory of the building. It lands cold, does real
work, and disappears when the container is reclaimed. Anything it learned that was not
written somewhere durable dies with it, and the next session pays to re-derive it. The
fix is not a bigger context window. It is a memory architecture: what gets written down,
in what shape, loaded when, by whom, and how a correction made once propagates to every
session after it.

This essay describes a working design that has run in production for weeks across a
multi-session fleet. Every mechanism below traces to a real failure it closed. The
airport metaphor is not decoration here; it turned out that the operational disciplines
airports and carriers invented for exactly this problem class (many independent actors,
shared state, no one person watching everything) port to agent memory almost one for one.

## The memory branch

Cross-session memory lives on an orphan git branch that is never checked out, never
merged, and carries no code. Git gives you everything the layer needs for free:
durability across container recycling, history, concurrent-writer safety via
fetch-and-retry, and read-on-demand instead of riding compaction summaries. The branch
has three parts:

- **A head file**, small and capped (about 120 lines), injected into every session at
  boot. Active threads, pending operator steps, parked items. Curated by one
  coordinator, never appended to by workers.
- **Saves**: dated full-fidelity exports (session distillates, design briefs, long
  arcs). Fetched on demand only, never injected. This is the backed-up-in-full half.
- **Fold files**: one append-only JSONL file per session, written only by that session.
  Nobody reads them directly; the fleet-wide view is computed at read time by a
  projection script. One session, one file, so N concurrent writers never contend.

Two rules keep the head small enough to inject. The **drain rule**: once an item lands
somewhere durable (a merged PR, a decisions-ledger entry, the handoff file), delete it
from the head; the durable copy is the reference. And the drain rule is **audited, not
just stated**: a report-only sweep flags head bullets whose every referenced PR has
merged, pointers to files that no longer exist, and expired broadcast lines. Findings go
to the coordinator to judge; the auditor never writes.

One implementation detail that cost a real bug: inject the head by **section, not by
line count**. A `head -40` style cap silently truncated the file below the section that
carried in-flight work state, so the lane the file existed to deliver never reached a
booting session. Print everything up to a named marker instead, and let the line cap on
the file itself be what bounds the injection.

## The fold protocol: completion is asserted, never inferred

The core failure this design closes: a merged PR is not a completion signal. It can land
part one of three, or ship a feature whose flag is still off. So **a merge proposes a
fold; it never folds**. A session that knows whether the thread is actually done records
a completion assertion deliberately, through a small CLI that enforces the honesty
rules:

- **A done-claim is refused while obligations dangle.** The checker is mechanical, not a
  judgment call: a "part N of M" with parts outstanding, a deferral marker in the diff,
  a feature flag that has not graduated to default-on, or an obligation the caller
  declared explicitly. Refused work is not lost: the same fold can be recorded as
  *parked*, with its open obligations attached, so state is captured without a false
  claim of done. A later done supersedes the park; a park dated after a done reopens the
  thread.
- **Every fold carries provenance, and "verified" is oracle-gated.** A fold names who
  asserted it, at what model tier, with what confidence. Claiming *verified* requires
  naming an objective oracle (a CI result, a data assertion, an operator ruling, a
  reverted PR) plus its evidence reference. Everything else is *asserted*, which the
  projection renders as "re-verify against the anchor before acting." A model can never
  promote its own claim.
- **Understandings need anchors.** A fold can also capture a frame-of-reference claim
  ("these two surfaces disagree about X") worth recalling later. It must anchor to real
  files, because an anchorless understanding is an unsourced assertion a later session
  cannot re-check.

## Decay and trust: what is still worth believing

Provenance becomes a rank, so an operator ruling outranks a cheap-tier claim by
construction rather than by file order: human ruling, then oracle-verified, then
asserted by a high-capability tier, then asserted by a working tier, then unattributed.
Rank orders the view; it does not hide anything. Only the unattributed rank is
quarantined, because that is the one case with nothing to weigh. Quarantining every
working-tier fold would quarantine most of the fleet's memory and train everyone to
ignore the lane, which is worse than no lane.

**Two kinds of forgetting, and they are not the same.** Never lose the durable: fold
files are append-only, and retirement means "stops being injected," never "is gone."
Deliberately decay the noise: a superseded claim, a resolved thread, an understanding
whose file moved on. A machine that cannot forget the noise is as useless as one that
forgets the signal. Decay is resolution-aware, not calendar-flat: state entries age out
on a short horizon, while an understanding gets a much longer one, because ageing a
hard-won understanding on a finished ticket's clock deletes exactly the recall the layer
exists to provide.

Because fold files are append-only, supersession is **forward-declared**: the new entry
names what it kills, in the same pointer grammar the decisions ledger already uses, so
the estate has one supersession syntax, not two. An unresolvable pointer is reported,
never silently ignored.

And the least-verified layer must never silently outrank the repo. Every anchor is
mechanically checkable: a path that is gone means *stale*; a file whose last commit
postdates the claim means *re-verify*. That second signal is the highest-value check in
the whole design, because "the file changed after you understood it" is precisely the
memory that misleads a future session, and it is invisible without the check.

**A third signal, later: decay by use, not just by rank or age.** Rank and age both
decide trust from the outside, what asserted it and how long ago. A newer signal
decides from the inside: does anyone actually rely on this entry. Stamp an entry each
time a session reads it and then genuinely acts on it, not just loads it. An entry
nobody has used in a long while becomes an archive candidate regardless of its rank; an
entry that keeps getting used earns another look even past its normal age-out horizon.
This catches what rank and age both miss: a high-ranked, recent entry that nobody has
actually needed since the day it landed is dead weight the same as a stale one, it just
hasn't been caught yet.

## The airport waves

The metaphor kept paying. Each of these is a discipline the aviation industry built for
distributed operations, ported to memory in a wave once the corresponding failure
showed up here.

**NOTAMs: fleet-wide broadcasts with mandatory expiry.** A directive scoped to the whole
fleet is broadcast into every session at boot. But a pilot's briefing is only useful if
conditions are current, so every broadcast requires an `until:` date. When it passes,
the boot hook silently drops the line; a genuinely permanent fact gets folded into the
decisions ledger and the broadcast retired. `until: standing` exists as a deliberate
escape valve, never a default. No open-ended NOTAMs: a stale broadcast is trusted advice
that has quietly gone wrong.

**MEL: the minimum equipment list.** Aircraft fly with known-inoperative equipment
because the MEL names it before takeoff. Every session boots with one line naming
known-broken gear (a missing key, an unavailable CLI, a dead test harness), so it plans
around inoperative items instead of rediscovering each one by failing at it.

**One screening checkpoint, every lane out of the building.** Sensitive-data screening
runs as a single detector applied at every outbound lane: memory-branch writes, email
drafts, file publishes, cloud writes. One pattern source, fail-closed on a hit. The gap
this closed is worth naming: plumbing-level pushes had bypassed the push-hook lint, so
the memory branch was unscreened until the screen moved into the write path itself.

**BRS: reconcile the claim against the manifest.** Baggage systems scan a bag's tag
against the aircraft manifest before loading rather than trusting the label. A
done-fold's "landed in PR N" pointer is a claim; the reaper greps the repo's own merged
history for that PR's squash commit and quarantines the fold on a miss. Fails open: an
unreachable lookup never manufactures a false quarantine.

**WorldTracer: match orphaned work to its claim.** Two independently-created records
for the same thing (a quiet unmerged branch, and a thread someone opened in memory) get
matched by a tiered algorithm instead of waiting for a human to notice one in `git
status`: exact slug match, then majority token overlap, then an unmatched report that
surfaces the branch's changed files so a human can read what is inside. Three buckets,
never a write: a branch matched to an active thread is a resurrection candidate; one
matched to a resolved thread is safe to flag for cleanup; unmatched needs a human look.
And unclaimed baggage escalates on a clock: an unmatched branch past a longer window is
broken out into its own section, so "just noticed" and "genuinely forgotten" read
differently instead of piling into one undifferentiated list.

**The mishandled rate: an SLA on claims, not just code.** Orphan matching catches
abandoned code; nothing in it catches an abandoned *claim*, a thread opened in memory
that never reaches done and sits in the layer indefinitely because nothing times it out.
Carriers track this as the mishandled-baggage rate; the same sweep computes it over
threads. Check-in is a thread's earliest fold; delivery is its latest fold when that
fold is a done. A thread past its SLA is mishandled and the report says so.

**Single-threaded ownership and tiered promises.** Two logistics principles close the
loop. Every parked thread requires exactly one named accountable owner, a person or a
session, never a committee; the tool refuses a park without one, because a dangling
obligation with nobody named is exactly the gap this closes. And not every thread gets
the same clock: a priority field (high, medium, low) picks the SLA tier, reusing the
task board's existing priority vocabulary rather than inventing a second one for the
same axis. When the named owner differs from the folding session, that fact *is* the
custody handoff, rendered explicitly as "owner X, handed off from Y." No separate
handoff mechanism exists on purpose; it would be the same fact recorded twice.

**The push layer.** A report that exists only when someone remembers to run it is not a
safeguard. The orphan sweep and the mishandled rate run inside the nightly scheduled
agent, so the reports arrive instead of waiting to be asked for. Report-only remains the
posture throughout: none of the sweeps writes a fold, retires a line, or deletes a
branch. The machinery surfaces; a human (or the accountable session) decides.

## The constitution underneath

Three rules hold the whole design together, and they are worth stating because every
future extension gets tested against them:

1. **Write partitioning.** One coordinator owns the head and the directives; each
   session owns exactly one fold file; workers never write each other's files. Safety by
   construction, not by locking.
2. **Derive, don't declare.** Anything a machine can compute from the durable record
   (fleet state, the projection, staleness, the mishandled rate) is computed at read
   time, never maintained by hand, so it cannot go stale and no session has to remember
   to describe itself.
3. **Humans move the dials.** Ranks, horizons, SLA defaults, and quarantine thresholds
   are constants a human changes on a review cadence. Nothing auto-tunes its own
   forgetting.

Start smaller than this. The first version was a single head file and a drain rule, and
that alone beat compaction summaries. Add the fold protocol when a merged-but-not-done
thread first burns you, decay when the head stops being skimmable, and the sweeps when
the fleet grows past what one person can watch. The waves came in the order the failures
did, and that is the right order for yours too.
