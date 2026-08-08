# Delivery protocol: diffs first, tests attached, questions bounded

**Assumes:** you run coding agents in a chat or session loop where their output lands in
your context window and their questions cost you a turn. Nothing else; the rules below
are paste-ready for any rules file.

Three rules about the SHAPE of what an agent hands back, not the content. Each one exists
because the default shape quietly taxes you: tokens on re-printed code, trust on
unverified changes, and turns on open-ended questions.

## The rules, paste-ready

```
- Diff-first delivery. Full file output is for NEW files only. A change to an
  existing file is delivered as a targeted edit or unified diff. Re-printing a
  500-line file for a 3-line fix spends context on the 497 lines that did not
  change and forces a visual hunt for the ones that did.
- No code without its check. A new module, route, or function ships with the
  test or runnable assertion that proves it, in the same delivery. Code whose
  verification is deferred is code whose verification is skipped.
- Bounded clarification. A clarifying question names 2 or 3 concrete options
  with a one-line trade-off each and a recommended pick, so it resolves in one
  reply. An open-ended "what would you like?" costs a round trip and usually
  comes back as one of the options anyway.
```

## Why each earns its place

**Diff-first.** The failure is invisible because it looks like thoroughness: the agent
re-prints the whole file "for clarity," the window fills with unchanged code, and three
exchanges later the session is compacting away the context that mattered. The tax lands
at the worst time and nothing attributes it to the re-print.

**Test attached.** "I will add tests after" is the deferral that never converts. Pairing
the check with the code in one delivery removes the gap where an unverified change gets
built on. This is the same stance as the verified-versus-asserted rule in the memory
layer: a claim is not done until something other than its author can say so.

**Bounded clarification.** Question density done right predicts SHORT sessions, not long
ones. A block of numbered options with recommendations resolves in one reply; a trickle
of open-ended questions across a session is the expensive pattern. The fuller treatment
of that finding is [docs/batched-decision-blocks.md](../docs/batched-decision-blocks.md);
this rule is its per-question form.

## What this deliberately does not say

No output format templates, no persona framing, no "you are an expert" preamble. Those
decay with context length and add boot weight. These three rules survive because each
binds at a delivery moment the agent already hits, which is the same placement logic the
rest of this kit runs on.
