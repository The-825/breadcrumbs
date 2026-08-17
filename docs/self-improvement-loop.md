# The self-improvement loop: refinement runs on evidence

The rules file, the conclusions store, and the command set are static
artifacts. What makes them compound is a loop that feeds real session
exhaust back into them. Without the loop, the rules file grows only when
something breaks badly enough to force a rule, and every smaller lesson
evaporates with the session that learned it. With the loop, the system gets
cheaper to operate every week, because the same mistake stops being paid
for twice.

One principle governs the whole loop: **refinement runs on evidence, not on
schedule.** Misses, denials, failures, and repeated friction are the inputs.
Periodically rewriting things that work is not maintenance, it is churn; a
retro that finds nothing changes nothing, and says so in one line.

## The loop, in three parts

1. **Instrument the exhaust (optional, cheap).** Session work throws off
   evidence for free; the only question is whether anything catches it.
   Three catchers have earned their keep in production, each a one-line
   append to a log file:
   - a **search-miss log**: every time a lookup (a where-is question, an
     index query, a docs search) comes back empty and the answer gets
     re-derived by hand, log what was asked and what finally answered it.
     Each row is a routing bug: the knowledge existed, the path to it did
     not.
   - a **flake ledger**: every test that passed on retry, logged even when
     nobody investigates it that day (the flake-ledger template in this
     kit).
   - a **command-use log**: when a slash command fights you (a wrong step,
     a dead pointer, a missing flag), one line saying which command and
     what the friction was.
   None of these are required to start. The arc itself (the diff, the PR,
   the conversation's own wrong turns) is evidence enough for a first
   retro.
2. **Run the retro at the end of an arc** (`templates/commands/retro.md`).
   It reads the evidence and classifies every lesson into exactly one bin:
   a conclusions append (something was re-derived that should have been
   known), a command or skill edit (the same friction happened twice), or a
   roadmap wishlist row (the arc invented a procedure worth encoding once
   it runs a second time). One lesson, one artifact, no double-filing, no
   "noted for later" without a file change.
3. **Let the artifacts do the compounding.** The conclusions store gets
   read at session start, so a captured lesson finds the next session that
   needs it. An edited command runs better the next hundred times it is
   invoked. A wishlist row waits with its evidence attached, so the day the
   procedure runs again the promotion decision is already argued.

## Why "exactly one artifact" is the load-bearing rule

The failure mode of retrospectives is producing insight instead of change:
a tidy list of lessons in a chat transcript, read once, lost. Forcing every
lesson into one durable artifact does two things. It makes the retro's cost
visible (a lesson not worth a one-line append was not a lesson), and it
makes the loop auditable: a month later, the conclusions store and the
command diffs ARE the record of what the system learned, with no separate
report to rot.

The single-bin rule also keeps the artifacts honest. A lesson filed as both
a conclusion and a command edit will drift into two versions; the one place
it lands is the one place future sessions trust.

## The other half: learning by looking, not only by breaking

Everything above is reactive by construction. Misses, denials, and failures
are the inputs, which is correct for refinement and leaves one gap: a system
that only learns from what breaks never learns what nobody has looked at.
The evidence for that gap is easy to gather in any mature repo. Take the
findings from your best exploration passes, the ones a person asked for, and
check what triggered them. If the valuable ones (a data source living where
nobody searched, a read path that was never built, a document describing a
subsystem that has since moved) were all triggered by somebody deciding to
go look, then exploration is running on attention, and attention goes where
the noise is. Quiet subsystems stay unexplored precisely because they are
quiet.

The fix is the same shape as the retro loop, pointed inward at your own
estate rather than at your own mistakes:

- **A coverage ledger.** One row per domain of the system, with when it was
  last explored and what a future session needs to know before re-exploring
  it. A domain never explored yet outranks any dated row, so every domain
  gets a first pass before any gets a second.
- **Rotation, never favorites.** The next pass takes the single stalest row.
  Hand-picking the interesting domain reproduces the attention bias the
  ledger exists to correct.
- **Explore with no target.** This is what makes it a different activity
  from an audit. You are not verifying a claim or chasing a bug: you are
  finding out what is true about the domain that nobody has written down.
  Sweep the live store for undocumented objects, cross-reference what the
  docs claim against what the system does, and specifically hunt for
  sub-areas with no instrument, no read path, or no documentation at all.
  An absent fact is a finding, the same as a wrong one.
- **Read-only, always.** A discovery pass captures; it never acts. Acting on
  a finding is separate, human-approved work. This is what makes an
  unattended pass safe to run at all.
- **Tag findings by origin.** Mark discovery-sourced entries distinctly from
  correction-sourced ones in whatever store they land in. That single tag
  turns "are we learning by looking or only by breaking" from a feeling into
  a count you can read per month.
- **A pass that finds nothing is a real result.** Record what was searched
  and why nothing surfaced. "Checked clean on this date" is worth having,
  and a rotation that only logs hits teaches sessions to manufacture them.

One caution worth stating, because it contradicts this doc's own governing
principle: this rotation IS scheduled, and that is deliberate. The evidence
rule exists to stop churn in artifacts that already work, while unexplored
territory generates no evidence by definition, so waiting for a trigger is
waiting forever. Keep the schedule slow and the passes cheap. A rotation
that fires so often it starts re-exploring fresh domains has turned back
into churn.

## Sizing it

Start with bin one only: run the retro command with no instrumentation and
land conclusions appends. Add the flake ledger when the first pass-on-retry
annoys you, the search-miss log when you notice the same where-is question
twice, the command-use log last. The loop is worth running from the first
week the rules file exists; the telemetry is worth adding only when the
evidence outgrows what memory of the arc supplies.

Add the inward-discovery rotation last of all, and only once the estate has
grown past what one person holds in their head. Below that size, you already
know which corners are unexplored, and a coverage ledger is bookkeeping for
a fact you have for free.

When you start logging corrections as evidence, admit them only when anchored
to an objective oracle, per
[templates/ledger-tools/CORRECTION_LEDGER_TEMPLATE.md](../templates/ledger-tools/CORRECTION_LEDGER_TEMPLATE.md),
so the loop cannot optimize a proxy.
