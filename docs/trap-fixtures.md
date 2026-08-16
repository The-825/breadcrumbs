# Trap fixtures: prove the memory rescues the model, with planted questions

ASSUMES an agent harness that injects your rules file into every session (most
do), and a repo whose rules file carries a handful of must-never-miss facts.
The probes run as read-only subagents; nothing here needs a framework.

## The failure this method catches

A memory system's docs can claim "sessions no longer miss X" without evidence.
The honest test is behavioral: plant the exact questions the system once got
wrong, run them cold, and grade deterministically. This is the systematized
form of a live incident, not a synthetic benchmark: every trap should be a
question that produced a REAL wrong answer before the safeguard existed.

## Design rules, learned by running it

1. **A truly bare condition is impossible.** If your harness injects the
   rules file automatically, every probe session carries your kernel whether
   you cue it or not. So the honest comparison is not memory-vs-no-memory; it
   is cue PLACEMENT: a prompt that explicitly points at the accuracy
   guardrails versus the same question asked plainly with the kernel merely
   ambient. Design for that comparison from the start instead of discovering
   it in the results.
2. **Fact-shaped traps cannot differentiate conditions.** A trap whose answer
   sits verbatim in the injected kernel passes in every condition, at every
   model tier. That is worth one run as evidence the kernel works, and
   nothing after. **Routing-shaped traps are the discriminating kind**: the
   answer lives two hops away, behind the map, where the failure mode is
   stopping at a plausible mirror instead of reaching the canonical source.
   In our first 16-run pass, the only head-to-head where the cue changed the
   outcome was a routing trap: the uncued run answered with a documentation
   mirror; the cued run hopped to the canonical definition and labeled the
   mirrors as mirrors.
3. **Grade deterministically, no LLM judge.** Require every probe reply to
   end with one line, `FINAL: <answer>`, and exact-match it against a
   pre-stated expected answer written down BEFORE the runs. A judge model
   grading trap answers reintroduces the vagueness the traps exist to remove.
4. **Record the wobbles, not just the verdicts.** One passing run opened with
   the wrong call and corrected itself by the FINAL line. That graded PASS
   under the pre-stated rule and still went into the report, because a reader
   skimming the top would have acted wrong. The qualitative row is where the
   next rule comes from (ours became: answer-first applies to the first
   sentence).
5. **Run the tier ladder.** The point of the memory system is that a light,
   cheap model navigates as surely as the heavy one. Run every trap at two
   tiers minimum. The light tier passing the once-failed question in every
   condition is the strongest before-and-after evidence the method produces.

## Cost and cadence

Each probe is one small read-only subagent; a 16-run pass (4 traps, 2
conditions, 2 tiers) costs roughly what one long feature session costs. Run
it on evidence of drift (a miss, a near-miss, a big kernel change), never on
a schedule; a scheduled run that always passes trains you to stop reading it.

## Drill the process, not just the recall

Trap fixtures test what a session KNOWS. The same fire-drill logic applies to
what the estate DOES, and the highest-value target is the machinery you have
never seen fire: conflict handling, escalation paths, automated recovery. The
failure mode is believing a doctrine works because it is written down. A
merge-conflict recipe, an automatic conflict notice, a peer-deconfliction
poke: each is machinery that sits dormant until the worst possible moment,
which is a real conflict on real work, discovers whether it was ever wired.

The conflict drill, the worked example: two branches edit the same line of a
dedicated drill file with different content, both open PRs, the first merges,
the second conflicts, deliberately. Then you watch, with a checklist rather
than hope: did the conflict get detected and announced by the machinery
(within what latency), did the announcement carry the resolution recipe the
doctrine promises, and did the owning session resolve it the way the rules
file says it must, without a human routing it. The drill file itself is the
record: each run appends one dated row stating what fired, how fast, and
what did not.

Design rules carry over from the traps almost unchanged. Drill against a
DEDICATED file, never real work, so the staged conflict costs nothing to
resolve either way. Run on evidence, not on a schedule: the trigger is a
change to the machinery being drilled (a new gate, a rewritten recipe, a new
notification path), because that is exactly when the written doctrine and
the wired behavior most plausibly disagree. And a drill that passes is not
noise: it is the difference between "the doctrine says" and "the doctrine
demonstrably does," which matters most on the machinery whose first real
test would otherwise be an emergency.

## Relation to the other measurement pieces

The forbidden-hit check in
[templates/ledger-tools/retrieval_exam.py](../templates/ledger-tools/retrieval_exam.py)
asks "can the superseded value still win retrieval"; trap fixtures ask "does
a live session, cold, land on the right answer to a question that once went
wrong." One tests the store, the other tests the whole path from boot to
answer. The process drill above extends the same question to the estate's
machinery. The measurement inventory around all of it is
[memory-measurement.md](memory-measurement.md).
