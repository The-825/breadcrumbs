# Breadcrumbs: cue-placement memory for AI agent fleets

*A working paper from one practitioner. Version 1.3, August 2026 (1.3 names Letta's
Context Repositories in section 6 and sharpens the axis from inspectable memory to
governed memory: git-backed storage is now shipped by others, which makes it the floor
rather than the claim. 1.0 published earlier
the same month; 1.1 extended section 3.5 with the tombstone, validity-window, and
audience-scoping mechanics that landed after publication, and added the Agent Memory
Atlas to related work; 1.2 adds the trust-timing fix the Atlas's own review of this
paper's system found, and notes the companion memory-desk kit's tooling maturing past
documented-but-not-executable). This describes a
pattern I run in production, generalized so you can run it too. The memory layer here
is a personal insight project, built on my own time out of my own need to stop
re-explaining context to my tools; it sits alongside the day job rather than being
part of it. It is not a product and there is nothing to buy; the companion artifacts
are in this repository under MIT.*

## Abstract

AI coding agents lose all working context between sessions. The dominant remedy is
retrieval: vector stores, knowledge graphs, and ranking layers that answer "what should
the agent remember?" Running many agent sessions a week against one production system,
I found retrieval was not my failure mode. My failures were governance failures: a
session claiming work was done when it was not, redoing work a previous session had
finished, or acting confidently on a fact that had changed underneath it. This paper
describes a different approach, borrowed from why an experienced traveler moves through
an unfamiliar airport almost as fast as a familiar one: place cues where the behavior
already happens, and let the environment do the remembering. Five mechanisms, all
implementable with git, shell hooks, and plain
text files: boot-time injection, refusal at the point of claim, oracle-gated
verification, versioned handoffs, and append-only supersession. I include the incident
that convinced me to publish, in which the system caught a false memory about itself,
and an explicit account of what I have not proven.

## 1. The problem is not recall

A fresh agent session pays a tax before any real work happens: re-reading files to
guess the current state, re-deriving decisions already made, being re-briefed by a
human who has explained the same context many times before. Bigger context windows and
better retrieval shrink parts of this tax, but three failure modes survive any amount
of recall, because they are failures of discipline, not of memory capacity:

1. **False completion.** A session reports "done" while an obligation still dangles: a
   follow-up unshipped, a migration half-applied, part two of three quietly dropped.
2. **Duplicate work.** A session redoes what a predecessor finished, because the
   predecessor's record of finishing was buried in a transcript nobody reads.
3. **Stale action.** A session acts on a fact that changed after it last looked, with
   no signal that the ground moved.

Retrieval systems make these worse in one specific way: they let the model write its
own confidence. A memory entry that says "verified" because the model felt sure is a
liability with a timestamp.

## 2. The design stance: cues, not archives

Drop a frequent flyer into an airport they have never set foot in and they still move
through it almost as fast as their home airport. Drop a first-time flyer into that same
building and they are anxious and slow, reading every sign twice, asking someone at
every junction. Same building, same signage, wildly different experience. The frequent
flyer is not fast because they memorized this particular airport. They are fast because
they learned how airports work as a system: what a sign means, what to ignore, what to
trust, where the pattern holds regardless of which building they are standing in.

The more useful observation is what happens to the first-timer by their second airport
of the same trip. Nobody hands them a manual between layovers. They do it once, notice
the pattern underneath the specific signs, and carry it forward. The second airport is
not easier because it is a simpler building; it is easier because they stopped treating
the first one as a one-off and started treating it as an instance of a system they now
understand. That gap, not a bigger map, is the design target here: not "give the agent
more to remember," but give the environment enough structure that any session, on its
first visit, moves like the experienced traveler.

Applied to agents: instead of building a smarter archive the agent must remember to
consult, place cues at the moments where agent behavior already happens, the way an
airport signs the next decision only, at the exact spot the decision gets made, and
gives the cues teeth. The moments are few and predictable: session start, finishing
work, claiming certainty, and handing off. Discipline is encoded as refusals rather
than reminders, because a reminder can be ignored and a refusal cannot.

## 2.5 This is not folk wisdom: the science underneath the signage

I arrived at cue placement by irritation, but the pattern has names, and I found them
after the fact, which I take as a good sign: the design converged on things that are
known to be true about memory in general.

**Cue-dependent memory.** The psychology of recall (Tulving's encoding specificity,
decades old and well replicated) says retrieval works best when the context at recall
matches the context at encoding. That is the literal mechanism behind the sign at the
gate rather than the map at the entrance. Boot injection works because it recreates the
working context, this repo, this branch, these open obligations, at the exact moment
recall is needed, instead of asking the agent to fetch it cold from an archive it has
to remember exists.

**Distributed cognition.** Studies of ship crews and airline cockpits (Hutchins,
*Cognition in the Wild*) found that the cognition of a working system does not live in
any one head; it lives in the ensemble of people and instruments. A pilot does not
remember the altitude. The altimeter holds it, and the pilot's competence is knowing
where to look. Underneath any terminal, the same distribution holds among the people
who run it: security only screens, they do not route luggage; ground crew only turns
planes around, they do not handle reservations; someone plans gate assignments hours
before a plane lands while someone else tracks a bag through three connections, and
none of them needs the whole picture to do their job well. That is the honest
description of what this system is: I am not giving an agent a better memory. I am
building a small cognitive system in which the memory does not have to live in the
agent at all, and a competent session is one that knows where to look.

**Prompts at the point of ability.** Behavior design (the Fogg model: behavior needs
motivation, ability, and a prompt arriving together) explains why reminders fail and
placed cues work. A reminder gambles that motivation will exist later, somewhere else.
A cue at session start fires at the moment of maximum ability, before the agent has
invested in any wrong path, which is why the door is the highest-leverage sign in the
terminal. And a refusal removes motivation from the equation entirely.

**Never trust, always verify.** Security engineering already has the vocabulary for
my oracle rule: zero trust. No claim is trusted because of who makes it, including
the system's own components; verification comes from an independent check or it is
not verification. An agent marking its own work "verified" is a self-signed
certificate, and it should be treated exactly the way you treat those.

**Organizational memory.** The literature on how institutions retain knowledge (Walsh
and Ungson's retention bins) observes that most knowledge loss happens because
knowledge lives only in individuals, and individuals leave. An agent fleet is the
pathological case: every individual leaves at the end of every session. So everything
has to live in the other bins, the procedures, the roles, the archives, which is why
the whole design keeps pushing memory out of the participants and into the structure.

### The hierarchy, and what self-actualization means for a memory

Reading the five mechanisms as a flat list undersells how they depend on each other.
They stack, and the stack runs in the same direction Maslow ran human needs: each
layer is only worth building once the one below it holds.

1. **Existence.** The memory survives at all: append-only records, nothing silently
   dropped. Without this, nothing above matters.
2. **Safety.** The memory cannot corrupt itself unrecoverably: refusal at the point of
   claim, supersession instead of editing in place, the wrong entry preserved under
   the correction that killed it.
3. **Belonging.** The memory is a shared grammar rather than a private diary: one join
   protocol that humans, and models of any make, enter through the same way.
4. **Esteem.** Standing in the memory is earned, never self-declared: the trust ladder,
   verification gated on named oracles, quarantine for the unattributable.
5. **Self-actualization.** The system becomes capable of maintaining its own
   integrity: it can audit its own beliefs against reality, discover that one of them
   is false, and correct the record while preserving the evidence of having been
   wrong.

The top of the hierarchy is not a feature I built. It is what the lower layers made
possible, and the case study that follows is what it looked like the first time the
system got there.

## 3. The five mechanisms

**3.1 Boot injection.** Every session starts with a small injected packet it did not
have to ask for: the short list of facts that must never be wrong (frozen verbatim and
pinned by a test, so a missing line fails a build), the open obligations no session has
finished, and a delta of what changed since this session last acted. The packet is
budgeted in bytes; injection is a tax every session pays, so everything injected has to
earn its place.

**3.2 Refusal at the claim.** A session cannot simply assert "done." It records a
completion claim, and the recorder refuses the claim while obligations dangle. The
session's options are to finish, to park the work with the leftovers explicitly
attached, or to formally defer a named item with an owner and a deadline, the way
aircraft operate under a minimum equipment list: a known-inoperative part is flown with
deliberately, on the record, with a due date, never silently.

**3.3 Oracle-gated verification.** No agent may mark its own claim "verified."
Verified status requires naming an objective oracle: a CI result, a data assertion
against a live store, a reverted change, a human ruling. Everything else is stamped
"asserted," and every future reader of an asserted entry sees an instruction to
re-verify before acting on it. Human rulings enter through the same grammar at the
highest trust rank, which makes humans and models the same kind of memory participant
at different prices, and makes the trust ladder legible: ruling over oracle-verified
over asserted, with unattributable claims quarantined.

**3.4 Versioned handoffs.** Shared memory state carries a version marker, and each
session acknowledges the version it booted on, the way pilots read back that they have
"information Bravo." Staleness becomes visible at a glance instead of surfacing as a
wrong decision. Session-to-session handoffs are written briefs with a replay guard:
read what your predecessor actually did before you redo it. Durable decisions are
written down in the same turn they are made, because a ruling that lives only in a
transcript gets re-litigated by the next session.

**3.5 Append-only supersession.** No memory entry is edited in place. A wrong entry is
killed by a newer entry that names it and explains the correction. The record of being
wrong survives, which is what makes the system auditable, and what made the incident
below tellable at all.

Three refinements landed after version 1.0 of this paper, all on the same principle:

- **Tombstones with redirects.** A correction that only overwrites is half a
  correction: the next session that re-derives the old value writes it right back.
  A rejected value gets a tombstone keyed on the value itself, with a mandatory
  reason; the store refuses to re-assert it until the tombstone is deliberately
  lifted, on the record. The tombstone can also name the value to use instead, so
  hitting it is a redirect rather than a dead end. And because a tombstone is only
  as good as retrieval honoring it, a standing forbidden-hit check asserts that a
  superseded value never wins the injection lane again; a hit is regression, not
  correction.
- **Validity windows.** A fact can be true for an era rather than forever. An entry
  may carry an optional valid-from and valid-until, so a session reasoning about a
  past period applies the rule that governed then, not today's, and asks the window
  instead of inferring it from supersession order.
- **Audience scoping.** Every fact carries a scope (public, internal, or regulated),
  and context assembly filters by the audience it is being built for, failing closed:
  an unscoped tier is omitted entirely rather than guessed at.
- **Verification timing, distinct from recording timing.** The Atlas's review of this
  system (section 6) found the sharpest gap in all of it here: a replay that asks
  "what did the memory know as of time T" checked only when a fact was recorded,
  never when it was verified, so a fact verified weeks later replayed as verified at
  any T in between, an oracle the session at T did not actually have. Verification now
  carries its own timestamp, and a replay before it shows the honest state, asserted,
  not verified. Ledgers written before the fix get a one-time soft backfill rather
  than a sudden, unearned trust drop: the best available signal stands in for the
  missing timestamp, flagged as inferred rather than observed, so the two are never
  confused later.

Two mechanisms outside this list matured the same month, in the lighter companion kit
this paper's own artifacts ship alongside (a settled-facts index rather than the full
supersession ledger above): a promotion step that was documented intent became
executable, and the staleness horizon stopped being one fixed number imposed on every
ledger and started reading each ledger's own re-check cadence instead. Neither changes
the five mechanisms; both close the gap between what the kit's own help text promised
and what it actually did.

## 4. Case study: the day it caught itself

This is the top of the hierarchy observed in the wild, once, in my one office: the
system holding a false belief about itself, discovering it through its own machinery,
and correcting the record without destroying the evidence.

In plain terms first, because the mechanics obscure how ordinary the failure was: I
wrote down that I had done something. I had not done it. Because my own written record
was wrong, every session had been quietly starting with less than half the memory it
was supposed to have, for days, and nothing complained.

The detail. There is a limit on how much of the memory files get loaded into each
session at startup, and a separate check that enforces that limit. I raised the limit
so sessions could carry more. In the permanent record I wrote that I had raised the
enforcing check to match. I had not. The check stayed at the old, smaller number, so
every session began loading its memory, hit the old limit, and was cut off partway
through. Nothing failed loudly; sessions simply started knowing less than they should
have.

Weeks later, a pass that reads every claim in the written record and compares it
against what the code actually does found the entry, checked it, and reported it false.
The entry had even pointed at the wrong file. That morning's own session startup was
the live evidence.

The fix took an hour: the guard resized from measured data, a test added that fails if
anyone shrinks the cap without re-measuring, and the false ledger entry superseded on
the record by a correction explaining exactly what was wrong. Nothing was deleted.

I offer this instead of a benchmark. The practical fear with agent memory is not
forgetting; it is confident false state. And the specific thing worth noticing is that
this was not a bug in code. It was a false entry in the documentation, which is a
harder problem, because a wrong note does not look wrong. Nothing normally checks a
written record against reality, which is exactly why bad documentation survives in
organizations for years. A system that can hold a false belief about itself, notice it
through its own machinery, and correct the record while keeping the evidence of having
been wrong, answers the real fear in a way a retrieval score cannot. It is also
difficult to fake, because the entire history sits in version control.

## 4.5 Auditing the archive: what eighteen months of my own sessions showed

The case study above is one incident. It is fair to ask whether the mechanisms address
anything more than the failure that produced them. So I did the obvious thing and had
never done: I exported eighteen months of my own session history, 216 conversations and
roughly 1,300 of my own turns, and read it as evidence rather than as nostalgia.

I recommend this to anyone building a memory system, and I want to be precise about why
it is not merely an interesting exercise. A memory design has two very different failure
modes that look identical from the inside. Either the store you needed does not exist,
or it exists and nobody used it. You cannot tell which from the design, and you cannot
tell from a single session. You can tell from the archive, because the archive records
what you actually asked for, over and over, and what you never once reached for. The
audit is the only instrument I have found that distinguishes a missing mechanism from an
unused one, and the two need opposite fixes.

The counts below are turn and thread counts, not impressions. They are unflattering on
purpose.

**Re-derivation is the dominant cost, and most of it had a home already.** Nine separate
threads across eight weeks re-derived the same question about how my tooling should be
arranged, each producing a recommendation, none producing a record the next thread could
read. The current version of a document corpus was re-established at least eleven times
across five threads, and the tell was the escalation: I kept widening the search radius
because the answer kept coming back incomplete. Basic identity facts were re-stated
across nine and eleven threads respectively. Nearly all of this belonged in stores I had
already built. The decisions ledger existed. The settled-facts store existed. Neither
carried this class of fact, because nothing classified "where should this kind of work
live" as ruling-shaped. That is an unused mechanism, and the fix is a trigger, not a new
store.

**Repeated corrections are specification bugs, and mine were legible.** One rule about
document voice was issued six times across five threads. The no-em-dash rule was issued
six times across three threads, including one explicit request to push it into the
generating prompts rather than apply it per artifact. That request landed and the rule
was still being applied by hand months later. My rules were enforced on code, by parse
checks and lint guards and CI, and not at all on generated documents. This is the
[specification debt](specification-debt.md) signal, and the archive is what made it
countable.

**A correction that does not survive regeneration is the single most expensive pattern
I found.** In one thread the same two corrections appear five times each, four of them
near-verbatim re-pastes with small clarifying additions. I was re-pasting because the
artifact was being rebuilt and the correction was not carried into the rebuild. A
project-scoped decisions ledger cannot catch this, because the correction is not
project-shaped, it is artifact-shaped. That was a genuinely missing mechanism, and it
became the [artifact correction ledger](artifact-correction-ledger.md).

**Boundaries leak in ways nobody logs.** Thirty-four bare "Continue" turns across twelve
threads, sixteen of them in a single thread. Every one is a resume from truncated state
where a partial deliverable can drop an item unnoticed. Fifty-one turns carried an
attachment and no text at all, so the intent lived only in the file and later
reconstruction had nothing to grip. Neither of these shows up in any conventional
measure of how a session went.

**The most useful finding was positive, which I did not expect.** The sessions that went
best all shared one structure: a numbered block of questions, each carrying a recommended
answer, blocking on a single reply. Twenty-five questions resolved in twenty-one turns.
Eighteen in fourteen. Twelve in nineteen. Seven in fourteen. Against that, the two worst
sessions in the archive carried six and sixteen questions across two hundred eighty-five
and one hundred six turns. Question density correlates with low turn count, which is the
opposite of the intuition, and the reason is that a block front-loads ambiguity into one
exchange instead of leaking it across fifty turns of rework. That pattern was emergent
and unnamed. Naming it is the whole intervention. It is written up as
[batched decision blocks](batched-decision-blocks.md).

The honest limits of this evidence. It is a retrospective self-audit by the person being
audited, on one operator's archive, and the counts measure how often I asked, not how
much any single ask cost. Most of the archive predates most of the mechanisms above, so
it measures the problem well and says almost nothing about the fix. What it establishes
is narrower than a result and more useful than an anecdote: the failures a cue-placement
design targets are real, frequent, and countable in ordinary work, and roughly half of
them were failures of a mechanism I already had and never pointed at the right corpus.

## 5. The join protocol

Nothing above depends, *by design*, on which model you run. A fleet member is anything
that can read a file at start and append a line at the end:

1. Read the boot packet. Mine is printed by a script; yours might be a `git show` plus
   a few greps.
2. Do the work.
3. Record what is now true as an append-only line in a file only you write: the claim,
   what anchors it, who you are, and whether an oracle verified it. Let the recorder
   refuse you if obligations dangle.
4. Read back the memory version you booted on, so staleness is visible.

The core loop touches no vendor API: a script that prints text, and an append to a
file. A human enters through the same protocol too, and my own rulings do exactly that,
at the top trust rank. Heterogeneous fleets are the design case, not an afterthought.

**What is tested, and what is not, because the distinction turns out to matter more
than I expected.** Models from two other vendors have read this system and reviewed it,
and that works. It is genuinely useful, in fact, precisely because an outside reader
brings assumptions the resident model does not, and catches things a session steeped in
the house conventions stops seeing. So cross-vendor *reading* is not a hypothetical
here; it is part of how the work actually gets checked.

What none of them have done is the write half. No non-Claude model has yet run the full
loop above, boot read through fold append through version ack, as a participating member
of the memory rather than a visitor commenting on it. The protocol is built to be
vendor-neutral and I believe it is, but belief is not a receipt, and this paper's own
standard is that a claim without an oracle is marked asserted rather than verified. So
the read side is verified and the write side is asserted, and I would rather say that
than blur the two.

One finding from the reading side is worth passing on, because it cuts against a naive
"any model, drop it in" reading. The models differ sharply in how well they follow the
pointer-based routing: one navigated it comfortably, another struggled enough that it
needed a separate, fully inlined copy of the rules written for it specifically,
subordinate to the original, before it stopped flagging deliberate patterns as bugs.
The storage protocol can be vendor-neutral while the *navigation* layer is not equally
legible to every model. Expect to write a capability-matched entry point per model
family rather than assuming one set of pointers serves all of them.

## 6. Related work, briefly and honestly

The retrieval tier (episodic and semantic memory stores with ranked recall) is mature
and well served by existing open-source and commercial systems; this paper takes no
position on which to use, because the pattern here sits beside them, not in place of
them.

Using git as a memory substrate is likewise not novel, and I make no claim to it. The
clearest instance is Letta's Context Repositories, shipped February 2026, which stores
a coding agent's context as files and, in their words, is "git-backed, so every change
to memory is automatically versioned with informative commit messages." That is the
same substrate choice made here, made independently and shipped inside a real runtime.
Anyone deciding between approaches on storage alone should look at theirs first: it is
integrated, it is maintained by a team, and it costs a slash command to turn on, where
this is a pattern you assemble yourself. Two open-source projects, Memoria and
GitAgent, occupy the same ground.

Which is the useful place to say what the substrate does and does not buy you.
Versioning answers what changed and when. It does not answer who was allowed to write
it, what had to be true before the write was accepted, or whether a correction actually
landed rather than being merely asserted. A perfectly versioned memory can be
confidently, durably wrong, and the commit log will faithfully record every step of it
being wrong.

What I have not found elsewhere, and what this paper is actually about, is the
governance layer: write-time refusal, verification gated on named oracles rather than
model confidence, obligation tracking with deadlines, versioned staleness signaling,
and append-only supersession, running together in one production system. Recent
academic work has begun naming the failure modes this layer answers (stale
propagation, contradiction persistence, provenance collapse), which I read as evidence
the layer is real rather than a private habit of mine.

There is a second comparison worth drawing, and it is not with a research system.
Consumer assistant products now ship cross-session memory by default, and it is the
version of this idea most readers have actually used. Asked to describe its own memory,
one such assistant reported holding summarized impressions of past conversations rather
than transcripts, updated in the background, with a search tool for retrieving older
chats when the summary came up short. That is a reasonable design and it optimizes for
the right thing for its use case: memory that costs the user nothing to maintain and
requires no discipline to keep working.

The trade it makes is visibility. A summarized impression cannot be diffed, dated, or
corrected in place. You cannot ask when a fact entered, what it superseded, or whether
it is still true, because the artifact holding it is not a document you can open. When
such a system is wrong about you, the repair path is to say so and hope the next
summarization pass absorbs it.

That is the axis this paper is actually on, and it is worth stating more precisely than
"agents forget between sessions." They increasingly do not forget, and increasingly they
store what they remember somewhere you could read. The question that survives both is
whether the memory is **governed**: whether a claim can be refused at the moment it is
written, whether calling something verified requires an oracle outside the writer, and
whether a correction is provably landed rather than merely announced. Inspectable is the
floor. Governed is the claim.

Three tests get you to the floor, and they apply to any memory system including the one
described here:

1. **Can you read it?** Not a summary of it, the actual stored artifact.
2. **Can you date it?** When did this enter, and what did it replace?
3. **Can a correction be verified as landed?** Not "I told it," but a durable record
   showing the old value retired and the new one in place.

A git-backed store passes the first two by construction. The third is where storage
stops helping, because it is not a question about the artifact, it is a question about
the process that wrote to it. That is the whole of section 3.

Every mechanism in section 3 exists to answer yes to those, and the cost is real: this
approach requires maintenance that an automatic summarizer does not. A reader whose
problem is convenience should use the automatic one. A reader who has been burned by an
agent acting confidently on a fact that changed underneath it is reading the right
paper, because that failure is invisible until you can audit the memory, and by then
the wrong action has already been taken.

The most useful single survey I have found is the
[Agent Memory Atlas](https://neoneye.github.io/agent-memory-atlas/), a field guide
analyzing 252 open-source agent memory systems and distilling them into named design
patterns. Its central thesis, that correction rather than retrieval is where memory
fails, is the same conclusion this paper's incident forced on me independently, and
that convergence is worth more than either claim alone. I mined its full catalog
programmatically and checked this system against it both ways: several of its
patterns turned out to be things already running here under other names
(evidence-before-belief, scope as a first-class key, correction reaching every
derived artifact), and several were genuine deltas I borrowed and shipped, including
the rejected-value tombstone's must-not-come-back test, keep-records so a reviewed
curation proposal is not re-proposed forever, a deliberate search for contradicting
evidence before asserting a positive, and a write guard under which a model-inferred
entry cannot silently supersede a human-stated one. Borrowing on the record is part
of the pattern too: each of those carries its source in the commit that landed it.
Its review of this system also found a real defect, the verification-timing gap
section 3.5 now describes, which is the useful kind of external review: not a score,
a place to look. After that fix landed I ran the Atlas's own seven-mechanism rubric
against this system myself rather than waiting for its next external pass, the same
inspect-trace-separate-synthesize method, pinned to a commit, published alongside
this paper. Self-review is not a substitute for the outside eye that found the gap in
the first place, and the writeup says so.

## 7. Limitations

This runs in one office, mine, at one scale, a few hundred agent sessions a month, in
one regulated domain, operated by the person who designed it. Evidence so far is
incidents caught and work not redone, counted by hand; instrumentation for measuring
which injected memories actually change behavior is new, and numbers from it will
follow rather than be promised. The instruments themselves are written up in
[memory-measurement.md](memory-measurement.md), so the method can be reviewed and run
elsewhere while the results are still owed. Structured handoffs are known from hospital
shift-change research to help the site that designed them more than adopting sites; I
assume that applies to me. Adversarial settings (a malicious fleet member poisoning
the shared record) are addressed only by the trust ladder's quarantine rank and the
append-only forensic trail, and deserve fuller treatment.

Two specific things I want to be unambiguous about, because both are easy to assume
from the design and neither is earned yet:

**Cross-vendor writing is asserted; cross-vendor reading is not.** See section 5. Models
from two other vendors read and review this system regularly, and that half works well
enough to be part of the process. No non-Claude model has yet run the full write loop as
a participating member of the memory, so the portability claim covers reading only until
that join is documented.

**This is one fleet, not many.** Everything here describes multiple sessions, over
time, sharing one memory for one system: one presence table, one memory branch, one
coordinator. It says nothing about two independently owned fleets staying continuous
with each other across a trust boundary. That is a genuinely harder problem, it is
not what I built, and I do not want the single-fleet result read as evidence for it.

**Nothing here internalizes anything, and that ceiling looks structural.** The whole
design gets a standard in front of every session, in identical words, without fail.
That is the stating half of a shared understanding, and it is more reliable than most
human teams manage, because it never gets skipped on a busy week. It buys nothing past
that. A person repeated at often enough eventually makes a principle their own and
starts applying it to cases nobody wrote down, including telling you when you are the
one getting it wrong. A session complies exactly and ends knowing nothing; the next one
starts from the same cold beginning. Total compliance and zero internalization are
different things, and only the first is on offer here. Plan the rest of the system
accordingly, because compliance covers the cases you already anticipated and nothing
else.

## 8. Try it

Start with one sign, not the whole terminal. Pick the single moment your agents most
often act on stale state and place one cue there that fires automatically; for me that
was session start. Add the refusal second, because it is the piece with teeth. The
copy-and-adapt artifacts (a session handoff file, a decisions ledger, a settled-facts
store, a bootable rules file, and a fail-closed merge gate) are in this repository,
MIT licensed. If you try the pattern and it breaks somewhere, open an issue and tell
me how: I am one investigator with one data point, and the pattern gets better the
more airports it runs in.

---

*Mr. Jovan Smith. Feedback, failed replications, and improvements are all welcome as
issues on this repository.*
