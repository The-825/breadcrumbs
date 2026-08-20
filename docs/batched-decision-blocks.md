# Batched decision blocks: ask twenty questions at once

> A companion to `decision-capture.md`. That doc covers writing a ruling down the turn it
> lands. This one covers how to get the rulings issued in the first place, cheaply, and it
> is the rare pattern I found by looking for what went right rather than what went wrong.
> **A working habit, not a mechanism: nothing here ships as code.**

## The finding, which is a positive one

Most of what an archive audit turns up is failure. You go looking for wasted turns and you
find them. This one came out the other way, and I am flagging that because a pattern
confirmed by successes is unusual enough to be worth trusting more than my instincts about
it.

I sorted eighteen months of sessions by how well they went and looked for shared structure
at the top. Every one of the best sessions had the same shape: at some early point the
agent stopped working, emitted a numbered block of questions with a recommended answer
attached to each, and blocked on a single reply.

The counts, which are the actual evidence:

- 25 questions resolved in 21 turns
- 18 questions in 14 turns
- 12 questions in 19 turns
- 7 questions in 14 turns

Now the other end. My two worst sessions carried 6 and 16 questions, across 285 and 106
turns.

Question density correlates with **low** turn count. That is backwards from the intuition,
which says a session full of questions is a session that is struggling. What the data
actually shows is that a session asking a lot of questions at once is a session that
gathered its ambiguity into one place. The 285-turn session was not question-free because
it was clear. It was question-poor because it kept guessing, and every guess bought a round
of rework.

## The mechanism

Ambiguity in a task is roughly fixed. You either pay it down in one batch up front, or it
leaks out one wrong assumption at a time across fifty turns of correction. The leaking
version costs more, and it costs more in the expensive currency: my attention, spent in
small unpredictable slices instead of one block I can sit down with.

The batch also changes what my reply has to be. Twenty-five questions with recommendations
attached is a reply of twenty-five short answers, many of them just "yes." Twenty-five
questions asked one per turn is twenty-five context reloads.

## The pattern

- **One numbered block, one blocking reply.** Numbered so answers can be terse and
  unambiguous. Blocking so the agent does not half-start on assumptions it is
  simultaneously asking about.
- **Every question carries a recommended answer.** This is the part that makes it cheap.
  A question with a recommendation is a yes-or-no. A list of options with no position hands
  the analysis back to me, which is the labor I was trying to delegate. If the agent cannot
  form a recommendation, that is worth saying, and it should say why in one line.
- **Ask early, before the work, not when stuck.** The block belongs after enough reading to
  know what is unclear and before enough building to have committed to answers.
- **Do not pad the block.** Density is a symptom of gathered ambiguity, not a target. Asking
  twenty-five questions to hit a number produces filler that trains me to skim, and a
  skimmed block is a block whose answers are guesses with my name on them.

A related result from the same archive: one session went unusually well because I opened by
asking to be interviewed. Same structure, initiated from the other side. That it works in
both directions is decent evidence the structure is doing the work rather than some quality
of the sessions that happened to use it.

## The side effect worth having

A question-and-answer block writes its own decision record. Twenty-five numbered questions
with my answers underneath is a complete, timestamped, in-context ledger of what was decided
and why, produced as a byproduct of the work rather than as a chore after it.

When I went back to reconstruct what happened in these sessions, the batched ones were by a
wide margin the easiest. The rulings sat in one block instead of scattered across two
hundred turns of conversational drift, and each one was legible next to the question it
answered. That was not why I started noticing the pattern, but it might be the better reason
to adopt it.

## What this does not solve

It front-loads ambiguity, so it fails on work where the questions are not knowable until
the work starts. Some tasks only reveal their real decisions once you are inside the data,
and demanding a question block up front on one of those produces a block of shallow
questions while the important ones stay hidden.

The honest move there is a short exploratory pass first, scoped and time-boxed, explicitly
to surface the decisions. Then the block. What does not work is skipping the block because
the task felt exploratory, which is the story my 285-turn session would tell about itself
if you asked it.
