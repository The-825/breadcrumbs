# Versioning is not governance

*What a git-backed memory gives you, what it does not, and how to tell which problem you
actually have.*

## The failure this is about

Your agent's memory is stored in git. Every change is a commit with a clear message. You
can read any fact, date it, diff it, and roll it back.

And it is wrong about something important, and has been for three weeks, and the commit
log records every step of it becoming wrong in perfect chronological order.

That is not a storage failure. Nothing was lost, corrupted, or hidden. A session wrote
something it had no business asserting, no gate stopped it, and every session since has
inherited it. Versioning gave you a flawless record of a bad write.

## What is actually shipped now

Storing agent memory in git is not a novel idea and it is not anyone's moat. Letta's
Context Repositories, shipped February 2026, stores a coding agent's context as files in a
repo and is, in their words, "git-backed, so every change to memory is automatically
versioned with informative commit messages." It is integrated into a real runtime, it is
maintained by a team, and you turn it on with a slash command. Memoria and GitAgent do
comparable things in open source.

If your problem is that your agent's memory is a black box you cannot open, go use one of
those. That is a solved problem and you should not solve it again yourself.

## What the substrate buys you, stated fairly

A git-backed memory gets you four things, and they are worth having:

- **Read the real artifact.** Not a summary of what the system believes, the thing itself.
- **Date it.** When did this enter, what did it replace.
- **Diff it.** See a change as a change rather than as a new state.
- **Branch and roll back.** Recover from a bad state, and let parallel agents work without
  clobbering each other.

Those are the first two tests in the breadcrumbs rubric, and a git substrate passes both
by construction.

## What it does not buy you

The third test is the one storage cannot answer: **can a correction be verified as
landed?** Not "I told it," but a durable record showing the old value retired and the new
one in place.

That is not a question about the artifact. It is a question about the process that writes
to it, and no storage format answers it. Three failure modes make the point, because all
three produce perfectly well-formed commits:

- **False completion.** A session reports done while an obligation dangles. The commit
  says done. Git has no opinion about whether it was.
- **Duplicate work.** A session redoes what a predecessor finished, because the record of
  finishing was somewhere it did not look. Two clean commits, same work, twice.
- **Stale action.** A session acts on a fact that changed after it last looked. The fact
  is correctly dated. Nobody checked the date.

Every one of these is a governance failure wearing a clean audit trail.

## The five mechanisms that do answer it

These are the governance layer, and each one exists because a specific failure got through
without it:

1. **Refusal at the point of claim.** A session cannot mark work verified by asserting it.
   The write is blocked, not warned about, which means it survives a cheap model on low
   effort that would have talked itself past a warning.
2. **Oracle-gated verification.** "Verified" requires naming an objective check that
   returned a result. Model confidence is not an oracle. Neither is a previous session's
   confidence.
3. **Obligation tracking with deadlines.** An unfinished commitment is a row with a due
   date, not a sentence in a transcript that scrolls away.
4. **Versioned staleness.** A fact carries when it was last checked and how often it needs
   rechecking, so acting on a stale value is a detectable condition rather than a silent
   one.
5. **Append-only supersession.** A correction retires the old value explicitly and leaves
   the retirement visible. Nothing is edited in place, so "what did we believe on the 3rd,
   and when did that stop being true" stays answerable.

Notice what these have in common: none of them are about where bytes live. They are all
constraints on writing. You can implement every one of them on top of a git-backed store,
and you should, because the substrate and the governance layer are complements rather than
competitors.

## How to tell which one you need

Ask what your last bad week actually looked like.

**Your memory was opaque and you could not see what it believed.** You need better
storage. Use a git-backed system, and you are close to done.

**Your memory was legible and still wrong, and nobody caught it until the damage was
visible.** Storage was never your problem. Adding versioning to it will give you an
excellent record of the same thing happening again.

The second case is rarer at first and it is the one that scales badly. One session with a
good memory is fine. Twenty sessions a week against one production system, some on cheap
models, some unattended, is where the difference between "I can read what it believes" and
"it cannot write something it has not earned" turns into real money.

## Where the artifacts are

Everything above runs in this repository under MIT, and nothing is for sale. The white
paper is [breadcrumbs-whitepaper.md](breadcrumbs-whitepaper.md), the mechanisms are
section 3, and the runnable pieces are `templates/memory-desk/` for the read side and
`ci-kit/guards/` for the refusal side, each guard shipping with fixtures that prove it
actually fires.

If you are running a git-backed memory today and the third test is the one you keep
failing, take the five mechanisms and leave the rest. They compose with what you have.
