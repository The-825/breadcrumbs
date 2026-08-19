# The skill nobody remembers to call

> Companion to [templates/standing-agents/skills-registry.md](../templates/standing-agents/skills-registry.md),
> which keeps a skill library from rotting. This one is about the other failure: a library
> that is perfectly healthy and quietly unused.

**What this assumes:** a repo with a library of reusable agent skills, commands, or
prompts, more than about a dozen, plus a harness that can run a hook on prompt submit and
a git history you can grep. Pattern only, no script ships with it; both pieces are twenty
lines against your own registry.

## The problem

You build a skill library because the work repeats. It works. You add more. Somewhere
between a dozen and two dozen entries, something changes that nobody notices for months:
**the only skills that get used are the ones already on the tip of your tongue.**

The rest are fine. The paths resolve, the selftests pass, a staleness gate says the library
is healthy. They just never fire, because invoking a skill requires remembering it exists
at the moment it applies, and human working memory tops out well below the size of a good
library. So the work gets done by hand, competently, slightly differently each time, by a
session that had a purpose-built tool available and no way to know.

This failure is invisible from every angle you would normally look. The library looks
maintained. The work looks done. Nothing errors.

## Two mechanisms

They pair: one makes the right skill easier to reach, the other measures whether that
worked.

### 1 · A trigger table, derived not written

Your registry already carries, for each skill, some description of when it applies. Derive
a trigger table from that field rather than hand-maintaining a second list, because a
hand-maintained parallel list is a thing that drifts the week after you build it.

Hook it to prompt submit. Match the incoming prompt against the table. On a hit, inject one
line: this skill exists, here is its name. Not the skill's content, not an instruction to
use it, just the existence and the name.

Two design notes that decide whether this is useful or annoying:

- **Silent on no match.** Most prompts will not match anything. A hook that says something
  every turn is a hook the session learns to skip, and then it is worse than nothing.
- **A hint can carry real data if the skill is read-only.** For a skill that only reads,
  you can run it behind a short cache and put its actual current answer in the hint instead
  of its name. A cache is what makes this affordable: without one you are paying a skill
  invocation on every prompt to serve a hint most prompts will ignore.

This is rung 3 of [the cue-placement ladder](cue-placement-ladder.md), applied to your own
tooling rather than to your rules.

### 2 · The gap detector

The hint makes skills reachable. This tells you whether anyone reached.

Cross-reference landed commits against each skill's declared trigger. When a commit's
subject or diff matches what a skill is for, and no invocation of that skill appears
anywhere near it, that is a candidate: work done by hand that had a tool.

Run it on a cadence, not on every commit. Read the output as a list of questions rather
than violations, because there are three legitimate reasons a match is not a miss:

- The skill genuinely did not fit this instance.
- The skill fits but is worse than doing it by hand, which is a finding about the skill.
- The skill's declared trigger is wrong, which is a finding about the registry.

All three are worth learning and none of them are failures of the person. The fourth case,
where the skill fit perfectly and nobody remembered it, is the one you built the detector
for, and it is usually the largest bucket.

## What to do with what it finds

**Do not respond by writing a document telling everyone to remember the skills.** That is
rung 5 answering a rung 3 problem, and it is exactly the reflex the ladder doc exists to
interrupt.

Respond by fixing the reachability. Better trigger phrasing, a hook that fires where the
work actually starts, or, for the small number of skills where doing it by hand is a real
risk, moving the check down to refusal so the by-hand path errors and names the skill.

And be willing to delete. A skill that never fires, whose trigger is right and whose fit is
good, is a skill nobody wanted. That is data too, and a smaller library that gets used
beats a comprehensive one that does not.

## What this is not

Not a productivity metric and not something to put on a dashboard. The output is a list of
questions about your own tooling, and the moment it becomes a number someone is measured
on, the number goes up and the tooling does not get better.
