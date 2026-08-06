# Specification debt: when a correction means your spec is wrong

> Sharper companion to `self-improvement-loop.md`. That essay says to mine each arc for
> lessons. This one names the specific signal that a lesson exists, and sets a threshold
> for acting on it without asking.

## The problem

You correct an agent. It fixes the thing. Next session, you correct it again. And again
next week. Each correction feels small enough to just handle, so it never gets written
down, and the correction cost repeats forever.

That is not a model failure. A repeated correction is evidence that your specification
is missing a rule. The agent is complying with what you wrote; what you wrote is
incomplete. Treating it as a chat event rather than a spec bug is the actual mistake,
and it is expensive precisely because each individual instance is cheap.

## The pattern

Count corrections. When the same one recurs past a threshold, patch the specification
automatically rather than asking permission.

- **Count across sessions, not within one.** Two corrections in a single conversation
  are one signal, not two: they reflect one bad output being worked on, not a durable
  pattern. The thing you are looking for is a correction that survives a session
  boundary, because that is what proves it is about your rules rather than about one
  response.
- **Three is a defensible threshold.** Once is noise. Twice is coincidence. Three times
  across three separate sessions is a missing rule, and the evidence is strong enough
  that stopping to ask permission wastes more time than a wrong patch would cost.
- **Auto-apply past the threshold.** If you require approval for each spec patch, the
  patching stops happening on the busy weeks, which are exactly the weeks generating
  the corrections. The whole point is to remove yourself from the loop.
- **Route by correction type, because they live in different files.** Tone and
  formatting go to your preferences. Behavior goes to the rules file. A wrong fact goes
  to the settled-facts store. A process complaint goes to your working agreements.
  Dumping all four into one file produces a document nobody can act on.

## Structure the ledger by the write path, not the read path

The non-obvious design decision, and the one worth stealing outright.

When you file a correction you already know which project you are in, and you are
deciding what kind of correction it is. When you later read the ledger, you are usually
asking "what keeps going wrong here." Both operations start from the project, so nest
project first, then correction type. Indexing by anything else means the person filing
has to think about retrieval, and filing is the step that has to stay frictionless or it
stops happening.

One exception worth building in: keep separate ledgers per domain, but share the count
for corrections that are universal. One occurrence in project A plus two in project B
still trips the threshold, because "you keep using the wrong tone" is a fact about you,
not about a project.

## What this does not solve

Detection across sessions is the hard part and it is not solved by writing the rule
down. Something has to actually notice that today's correction matches two from previous
weeks, and a fresh session has no memory of either. In practice this means the counting
has to live in the durable store the session reads at boot (see `floating-memory.md`),
and the agent has to be told to check it. If you build the ledger without the detection,
you get an accurate archive of corrections nobody acts on, which is worse than nothing
because it feels like progress.

Start by counting by hand for a month. If the same three corrections show up, you did
not need the automation to learn the lesson, and you now know exactly which three rules
your spec is missing.
