# The agent-ops operating model

Agent-assisted development has a default failure mode, and it is not bad code.
It is fast, plausible, inconsistent work where every session is a cold start,
discipline decays under velocity, and everything the agent learned lives in
transcripts that evaporate. Each individual session looks productive. The system
as a whole forgets, contradicts itself, and quietly lowers its own standards.
This essay is the operating model that counters it: six commitments and the
order to adopt them in. Every other file in this kit is one of these commitments
made copy-pasteable.

## Patterns over snowflakes

Codify a pattern once, and new work becomes composing existing pieces. The first
table renderer, the first route shape, the first query idiom: build each one
deliberately, extract it, and every later feature reuses it. The alternative is
a codebase of snowflakes, where every page invented its own markup and every
endpoint its own error shape, and where an agent asked to "add a page like the
others" has no "others" to pattern-match against.

The working rule: if you catch yourself (or your agent) reinventing markup, a
route shape, or a query idiom, stop and extract. The extraction is never wasted,
because the third use always comes. And an agent is dramatically better at
"compose these existing pieces" than at "invent something consistent with a
codebase of inconsistencies." Patterns are what make delegation safe.

## Infrastructure or a feature, never both

Every PR ships infrastructure OR a user-visible improvement. Not both. This
sounds like bureaucracy until you watch what mixing them does.

Force-multiplier work (the test harness, the lint guard, the config registry,
the CI gate) compounds. Every later PR inherits it. But it only compounds when
it lands as its own reviewed, named, revertable unit. Buried inside a feature
diff, the harness change gets no review, no visibility, and no identity: six
months later nobody knows it exists, so nobody extends it, and the next person
builds a second one. Meanwhile the feature it was buried with cannot be reverted
without taking the infrastructure down.

Decompose them. The infrastructure PR is small, boring, and merges fast. The
feature PR that follows is smaller than it would have been, because the
infrastructure already exists. Both get reviewed as what they are.

## Catch regressions at the lowest layer that can catch them

Every class of failure has a cheapest gate that can detect it. Route the failure
there.

- Parse-time errors: syntax checks. `node --check`, a Python compile, a YAML
  parse. Cost: about one second.
- Runtime and UI breakage: a handful of browser smoke specs per page.
- Data integrity: declarative assertions in the view layer, queries that must
  return zero rows, wired into a real run gate.
- Business logic: unit tests.
- The whole surface: a route smoke that boots the app with faked dependencies
  and sweeps every read route.
- The deploy: test-gated, with a post-deploy health check. A red test blocks the
  rollout.

The point of the layering is economic. A one-second parse check that catches a
typo saves a human review round, a CI cycle, or a production incident, whichever
expensive layer would have caught it instead. And each layer, once built, runs
on every PR forever. Coverage compounds: at fifty smoke specs, every PR is
regression-tested against all fifty, including the forty-nine written for other
features. This matters double with agents, because agents produce diffs faster
than humans can deeply review them. The layers are what make that throughput
safe to accept.

## Capture it the turn it lands

Agent sessions are amnesiac by default. Whatever a session learned, decided, or
was told exists only in that session's transcript, and the transcript
evaporates. The counter is a capture rule with a strict trigger: the same turn,
not the end of the session.

Two kinds of knowledge get captured, into two different files. Operator rulings
(a definition, a threshold, a policy fact, a display convention) go in the
decisions ledger, append-only, with the ruling, one line of why, and where it
landed. Discovered facts (a gotcha, a verified root cause, a domain fact that
took an hour to establish) go in the conclusions store, path-keyed so a future
session working on that file finds them.

Why the same turn: a session can end or compact before an end-of-session summary
is ever written. Capture-on-the-event beats capture-on-a-schedule every time the
schedule would have been too late. A ruling that lives only in a transcript does
not reach the next session; it gets re-litigated or silently violated. Both
outcomes cost more than the thirty seconds the capture took.

## The session-state handoff

The continuity spine of the whole model is one small file at repo root: the
session-state handoff. It holds what is in flight right now: the active branch,
the open PR, uncommitted edits by path, numbered next steps, decisions waiting
on the operator. It is refreshed on an explicit trigger word, and it is short by
design, because it is a handoff, not a log.

With the handoff, a new session boots from written state instead of re-deriving
context or trusting a lossy auto-summary. Mid-work model switches become safe:
checkpoint first, then the next model picks up mid-flight. Finished work moves
out to the changelog so the file never grows into history.

The handoff completes a memory architecture where every layer has one job. The
rules file holds the rules. The handoff holds the rolling state. The decisions
ledger holds operator rulings. The conclusions store holds settled discovered
facts. The known-issues ledger holds numbered open problems that are never
silently dropped. Content moves between layers on defined events: a checkpoint,
a ruling landing, an issue surfacing. When each layer has one job, a session
knows exactly where to look and exactly where to write.

## The quality floor never decays

The most dangerous sentence in agent-assisted development is "it's just a small
fix." Small fixes are where the security floor erodes, because every gate feels
disproportionate to a two-line diff. Parameterized queries, auth at the
boundary, no silent failures, forward-only migrations: each one survives the big
PRs, where scrutiny is high, and dies in the small ones, where it is not.

So the floor is stated as a floor: it applies to every diff regardless of size,
and to every agent regardless of tier. If a subagent or a cheaper model would
default to lower discipline on a small fix, that default is wrong for the repo,
and the rules file says so in exactly those words. Production discipline is a
property of the repo, not of the diff or of whoever happens to be holding the
keyboard. The rules that enforce this are cheap to follow and expensive to
retrofit, which is why they are commit-time rules and not cleanup-sprint
aspirations.

## Verification is the culture, not a step

Threaded through all six commitments is one posture: verify before you act on a
belief. Verify against the live store before authoring a query. Verify the diff
before pushing it. Verify every citing surface after changing a fact. And after
any burst of fast delegation, commission an audit of the last several PRs,
because velocity outruns verification exactly once before you learn to schedule
the audit.

An agent will confidently act on a stale assumption forever. The operating model
works because every assumption has a cheap check, and the checks are habits, not
heroics.

## Adopt in this order

Each step works without the ones after it, so stop wherever your setup stops
hurting.

1. **The rules file.** Start here; everything else assumes it exists.
   [../templates/CLAUDE_TEMPLATE.md](../templates/CLAUDE_TEMPLATE.md)
2. **The session-state handoff.** The single highest-value file per minute of
   setup.
   [../templates/SESSION_STATE_TEMPLATE.md](../templates/SESSION_STATE_TEMPLATE.md)
3. **The decisions ledger.** Stops re-litigation the first week you use it.
   [../templates/DECISIONS_TEMPLATE.md](../templates/DECISIONS_TEMPLATE.md)
4. **The conclusions store.** Adds the discovered-facts layer once sessions
   start finding things worth keeping.
   [../templates/CONCLUSIONS_TEMPLATE.md](../templates/CONCLUSIONS_TEMPLATE.md)
5. **PR discipline.** Shape the units of work before you speed them up.
   [../checklists/pr-discipline.md](../checklists/pr-discipline.md)
6. **The pre-push check.** Thirty seconds that buys back whole review cycles.
   [../checklists/pre-push.md](../checklists/pre-push.md)
7. **The continuity sweep.** Once your facts have multiple citing surfaces,
   this is what keeps them agreeing.
   [../checklists/continuity-sweep.md](../checklists/continuity-sweep.md)
8. **Session efficiency.** Cut the token and attention budget once the
   structure is in place.
   [../skills/agent-session-efficiency.md](../skills/agent-session-efficiency.md)
9. **Regression layering.** Build the gates as the codebase grows into needing
   them. [../skills/regression-layering.md](../skills/regression-layering.md)
10. **The flag lifecycle.** Last because it pays off most once you are shipping
    user-visible features on a cadence.
    [../skills/feature-flag-lifecycle.md](../skills/feature-flag-lifecycle.md)

## The build ladder: verify at the cheapest surface that can answer

A companion habit to lowest-layer testing, for the BUILD side. When a task can
be verified at several surfaces, work them in cost order: verify claims in the
SOURCE first (read the code or config that owns the fact), then at the DATA
layer (a query against the store of record), then in a cheap ARTIFACT REPLICA
(an in-process harness, a local render, a synthetic fixture), and only last in
the full APP SURFACE (boot the product, click the flow). Each rung is an order
of magnitude cheaper than the next, and most questions die on the first two.
The anti-pattern this replaces is reaching for the app surface first because it
is the most literal: booting the product to answer a question the config file
already answers. Agents fall into it more readily than humans, because to an
agent every surface costs the same number of keystrokes; the ladder is what
keeps verification spend proportional to the question.

Put a human go-gate between the data rung and everything above it, and make
the gate concrete: present the query together with its EXPECTED row count,
and get agreement on both before any interface work exists. A population that
is wrong by a factor of two is obvious in a single number and nearly
invisible once it is rendered as a chart somebody is already reacting to.
That one number is the cheapest correctness check in the whole ladder, and
skipping it is how a polished surface ends up confidently reporting the wrong
denominator.

Three delivery conventions ride along the last rung, and they are what keep
the output from becoming its own mess. Write deliverables straight to their
canonical destination instead of handing over loose files a human then
re-files, because the loose-file habit is precisely what produces the shared
folder nobody can navigate. Give every recurring outbound message a template
rather than drafting it fresh each time. And when a cycle or a season
concludes, archive its artifacts instead of leaving them on an active
surface, so what is live stays legible.

The model is not a way to slow agents down. It is what lets you go fast without
the system forgetting, drifting, or eroding underneath you.

