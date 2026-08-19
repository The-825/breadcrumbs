# The cue-placement ladder

> The framework the rest of this repo's memory docs are instances of.
> [chorus.md](chorus.md) is the top rung, [catalog-routing.md](catalog-routing.md) is the
> bottom one, and [breadcrumbs-whitepaper.md](breadcrumbs-whitepaper.md) argues the
> underlying principle. This is the part that tells you which rung a given rule belongs on,
> and when to move it.

**What this assumes:** a repo where agent sessions read a rules file, and a harness that
can inject text at session start, at each turn, or at a tool call. If your harness has no
hooks you can still use the top and bottom rungs, and the ladder still tells you which
rules deserve the expensive treatment. Pattern only: nothing in this doc ships as a script.

## The problem

You wrote the rule down. It is in the rules file. Every session loads that file. The
session broke the rule anyway.

The reflex is to write it again, louder, higher up the file, in bold. That occasionally
works and usually does not, because the problem was never that the rule was absent. It was
that the rule was present at session start and the decision happened forty minutes later,
in a different frame, with the relevant paragraph three thousand tokens behind the model's
attention.

**Presence in the context window is not salience at the point of decision.** Those are
different properties and only one of them protects you.

## The ladder

Five places a rule can live, ordered by how much each depends on the model remembering
something. Lower rungs survive a cheaper model on a bad day. Higher rungs are cheap to
add and easy to miss.

**Rung 1. Refusal.** The action is mechanically blocked. There is nothing to remember,
because the system does not permit the thing. A pre-commit hook that rejects the write. A
tool call that errors. A guard in CI that fails the build. Costs the most to build and is
the only rung that holds when the model is wrong about everything else.

**Rung 2. Cue at the action.** Text injected at the moment of the specific tool call, so
the rule arrives while the action is being taken rather than before it was contemplated.
"You are about to edit a file in this directory; here is the one thing that bites here."

**Rung 3. Cue at the turn.** Text injected on every prompt, usually matched against what
the prompt is about. Fires often, so it must be short and it must be quiet when it does not
match, or it becomes noise the session learns to skip.

**Rung 4. Cue at the door.** Session-start injection. The frozen facts, the handoff, the
current state. Reliable for framing, unreliable for a decision that happens much later in a
long session.

**Rung 5. Reference on request.** The docs, the catalog, the essays. Reached only if
something routes the session there. Excellent for depth, useless for anything the session
does not know to look up.

**The rule for using the ladder: push any rule that protects against an invisible failure
as far down as it will go.** Invisible is the operative word. A rule whose violation is
loud and immediate can live at rung 5, because the failure teaches the lesson itself. A
rule whose violation looks exactly like success needs rung 1 or 2, because nothing will
teach it.

## The curriculum

The ladder says where a rule lives. This says how hard the corpus works to keep it.

**Recited.** Repeated verbatim, every session, never reworded, held by a test. Reserve this
for the handful of facts where a miss produces a wrong answer or an unsafe write. The cost
is real: it is paid on every single session forever, so the list stays short or it stops
being special.

**Applied.** Not recited, but fired by a hook at the moment it is relevant. The bulk of
real operating knowledge belongs here.

**Reasoned.** Not injected at all. The session works it out from an invariant it does know,
and gets it right because the invariant is well chosen.

**Referenced.** Lives in the corpus. Reached on demand, and that is fine.

## The promotion rule

This is the part that keeps the whole thing from inflating.

**A fact moves up a level only when a real miss proves its current placement failed.**

Not because it seems important. Not because someone was nervous about it. A documented
instance where a session had the rule available at its current level and missed it anyway.

Without that rule, every fact anyone ever worried about migrates to the top, the recited
list grows to forty lines, the session skims it, and you have paid the cost of rung 4 while
getting the reliability of rung 5. The promotion rule is what makes the expensive rungs stay
expensive and therefore stay effective.

Demotion is allowed on the same evidence standard and almost never happens, which is worth
noticing about yourself.

## Worked example

A team keeps getting orders written with the wrong currency code on a multi-region store.

Rung 5, where it starts: a line in the data conventions doc. Sessions that read the doc get
it right. Sessions that do not, do not.

Rung 4: it moves into the rules file, loaded every session. Better. Still missed in long
sessions where the write happens late.

Rung 2 after the second real miss: a hook on writes to the orders module injects one line
naming the currency rule. Now it arrives at the moment of the write.

Rung 1 when a miss reaches production: the schema rejects an order whose currency does not
match its region. Nothing to remember.

Notice that each promotion was paid for by a real failure, and that the team did not jump
to rung 1 on day one. Rung 1 is the most expensive to build and the most annoying to live
with, and most rules never earn it.

## What this is not

Not a maturity model, and there is no prize for having everything at rung 1. Most rules
should live at rungs 3 through 5 forever. The ladder is a tool for the specific moment when
a rule keeps getting missed and you are deciding what to do about it, and its main
contribution is telling you that writing it down again is not the answer.
