# The artifact correction ledger: bind the fix to the thing, not the chat

> Companion to `specification-debt.md`, and deliberately not the same pattern. That doc
> handles corrections that recur across projects and prove your rules are incomplete.
> This one handles a single correction that will not survive its own deliverable being
> rebuilt. **Pattern only: the ledger is a file you keep, not a tool that ships here.**

## The problem

I went back through eighteen months of my own session archive looking for wasted turns.
The clearest one: in a single thread, I issued the same two corrections five times each.
Four of the five were near-verbatim re-pastes of the earlier text with a small clarifying
addition tacked on, as though saying it more precisely was the missing ingredient.

It was not. The corrections were fine. The problem was that each one was attached to a
conversation, and the deliverable kept getting regenerated. Every rebuild started from the
original instructions and produced the original mistake, so I pasted the fix again. I was
acting as the storage layer, badly, at full price.

A second case in the same archive is worse because nothing about it looked like friction.
A ruling had been made about which population basis was canonical. Later, a newly supplied
document assumed the other basis, and the ruling silently reverted. Nobody re-litigated it
and nobody argued. The output just quietly changed underneath, and it surfaced only
because someone happened to ask a question that touched it.

Both are the same failure. A correction lives in a transcript. The artifact does not read
the transcript.

## How this differs from specification debt

Worth being sharp about, because the two look alike and the wrong store fixes neither.

Specification debt is a **frequency** signal. The same correction shows up in three
different projects, and the conclusion is that a rule is missing from your spec. The fix
goes into the rules file and applies to everything you build afterward.

This is a **persistence** signal. The correction may only ever apply to one document, and
it may have been issued exactly once and accepted immediately. It still gets lost, because
the thing it applies to gets rebuilt from a source that never learned it. The fix has to
travel with that one artifact.

A project-scoped decisions ledger does not catch this. I had one. It is keyed by project
and it worked as designed, which is the point: nothing in a regeneration path knows to
consult it, and nothing in it is addressed to the file being regenerated. You can read a
decisions ledger and still not know which of its forty entries constrain the memo you are
about to rewrite. Different failure, different store, different key.

## The pattern

Every accepted correction on a deliverable gets appended to a list bound to that
deliverable's identity, and the list gets replayed before the deliverable is rebuilt.

- **Key by artifact, not by session or project.** The record is `report-q3-summary`, not
  "the Tuesday thread." That key is what lets a regeneration six weeks later, in a session
  that remembers nothing, find the corrections that apply to exactly what it is about to
  produce.
- **Append on acceptance, not on utterance.** The trigger is me saying yes to a fix, not me
  floating an idea. A ledger that captures every passing thought gets ignored inside a
  month, and an ignored ledger is worse than none because it looks like coverage.
- **Replay before generating, not after.** The corrections load as constraints alongside the
  original instructions. This is the whole mechanism. Everything else in the pattern is
  bookkeeping in service of this one step.
- **Diff every regeneration against the last accepted version, and report what changed.**
  This is what catches the silent revert. A new input document that quietly flips a settled
  ruling shows up as a line in a change report instead of as a number nobody questions. The
  report does not need to be smart. It needs to exist.
- **Keep entries short and imperative.** "Population basis is the enrollment census, not the
  application file." One line, no history, no justification. A correction ledger that grows
  paragraphs stops being replayable, and replay is the only thing it is for.

## What this does not solve

It requires a stable artifact identity, and that is a real constraint rather than a
footnote. If you regenerate under a new filename every time, or paste the output into a
fresh document, or let each rebuild live in whatever thread you happened to be in, the
ledger has nothing to bind to and you get exactly nothing from it. The discipline of naming
the thing and keeping the name is the price of entry.

It also does nothing about corrections you never accepted out loud. Plenty of my rework
came from vague dissatisfaction that resolved into a better draft without any moment I
could point to and file. Those stay lost. I do not have a fix for that, and I am suspicious
of any design that claims one, because inferring an accepted correction from a tone shift
is how a ledger fills up with things I never agreed to.

Start by keeping the list for one deliverable you rebuild often. If the replay stops you
re-pasting a single correction twice, it has already paid for itself.
