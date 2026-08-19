# Governing agents that act

> The operational half of [breadcrumbs-whitepaper.md](breadcrumbs-whitepaper.md). The
> paper argues that the hard problem is governance rather than recall, and describes the
> five mechanisms that answer it. This is the same argument turned outward: what to log,
> what an agent may never decide alone, how to prove afterward what it did, and a
> self-assessment you can run on your own deployment in twenty minutes. Pairs with
> [versioning-is-not-governance.md](versioning-is-not-governance.md), which is the
> shorter argument for someone who already stores agent memory in git.

**What this assumes:** an agent that takes actions rather than only producing suggestions,
running against systems or data where being wrong has a consequence outside your team. It
is not about model selection, and it does not assume any particular stack, framework, or
vendor. If nothing of yours is in production yet, this is premature and you should build
first.

## Who this is for

You are deploying, or have already deployed, an agent that does something rather than
suggests something. It reads records, drafts documents, routes requests, updates systems,
answers people. Someone will eventually ask you what it did and why, and that someone may
be an auditor, a regulator, a customer's procurement team, or a person who was affected by
an answer it gave.

This is about being able to answer that question.

## The premise

**The failure mode is not that the agent is wrong. It is that the agent is wrong in a way
that looks exactly like being right.**

Models are now good enough that the obvious failures are rare. What survives is a class of
failure that produces clean, well-formed, confident output:

- **False completion.** The agent reports the task done while an obligation is still open.
  The record says done. Nothing in the record is false, and the work is not finished.
- **Duplicate action.** The agent redoes something a previous run already did, because the
  record of the first run was somewhere it did not look. Two clean logs, one job, twice.
- **Stale action.** The agent acts on a fact that changed after it last looked. The fact is
  correctly stored and correctly dated. Nobody checked the date.
- **Unearned assertion.** The agent states something as verified because it is confident,
  not because anything checked.

None of these are model failures and none of them are fixed by better prompts. They are
failures of process, and they stay invisible until the consequence surfaces, which is the
worst available moment to find out.

## The four questions

Every deployment has to answer these. Most answer two.

1. **What did it do?** Not a summary. The actual record of the actual actions.
2. **Why did it do that?** What was true, and known, at the moment it decided.
3. **What was it not allowed to do?** And is that a rule the system enforces, or a rule
   written in a document the agent may or may not have read.
4. **When you found out it was wrong, did the correction land?** Provably, durably, and
   surviving the next time the system rebuilds itself.

Question 4 is the one nearly everyone fails, and it is the one that separates an incident
from a pattern.

---

## 1 · What to log

The instinct is to log everything, which produces a volume nobody reads and a bill nobody
wants. Log for the question you will be asked, not for completeness.

**Log the decision, not just the output.** The output is recoverable. What is not
recoverable later is what the agent knew when it acted: which records it read, which rules
were in force, which version of the instructions it was running. An output without its
inputs cannot be re-examined, only re-run, and re-running gives you today's answer to
yesterday's question.

**Log refusals and near-misses, not only actions.** A system that logs only what happened
cannot tell you what it stopped. Refusals are the evidence your controls work, and they are
the first thing anyone assessing the deployment will ask to see.

**Timestamp what was checked separately from what was recorded.** These are different facts,
and conflating them is the root of stale action. "This was true on the 3rd" and "we last
confirmed this on the 3rd" mean different things in June.

**Distinguish checked-and-false from could-not-check.** A two-state result field is a bug
waiting to happen. False because it was evaluated and false is a different world from false
because the check errored, and a system that stores both as false will act confidently on a
check that never ran.

**Never log the sensitive payload.** Log that a record was read, by whom, under what
authority, and for what purpose. Do not log its contents. An audit trail that becomes its
own breach is a net loss, and this is the most common way a well-intentioned logging policy
makes things worse.

## 2 · What an agent may never decide alone

The useful version of this is not a list of forbidden topics. It is a test you can apply to
any proposed action.

**An agent may not make a decision whose reversal costs more than its correct execution
saves.**

That single line does more work than a topic list, because it scales with your actual risk
rather than with whatever someone imagined when the policy was written.

Four categories fail that test in nearly every organization:

- **Anything that terminates a person's status or eligibility.** Ending, denying, removing,
  disqualifying. The asymmetry is total: a wrong grant is recoverable, a wrong denial often
  is not, because the affected person usually does not know to appeal.
- **Anything that moves money or creates an obligation.** Including small amounts, since
  reputational cost is not proportional to the dollar figure.
- **Anything that communicates externally under your name.** An agent may draft. A person
  sends. The moment that inverts, your organization's voice is a model's output.
- **Anything that deletes.** Soft-delete is not a compromise here, it is the correct design.
  Recoverability is the property that matters, not whether a row is visible.

**The enforcement question is the real question.** A rule an agent is told is a rule an
agent can talk itself past, and a cheaper model on a busy day will. A rule the system
enforces holds regardless of what the model believes. Whenever a rule protects against a
failure you would not notice, push it from told to enforced. The cue ladder in the white
paper is the same idea stated as a design order.

## 3 · Proving it afterward

**Nothing marks its own homework.** An agent may not record its own work as verified. To
call something verified it must name an external check that ran and returned a result.
Model confidence is not evidence, and neither is a previous run's confidence, which is how
an unearned assertion becomes institutional truth.

**Corrections are events, not edits.** When something is found wrong, do not overwrite it.
Record that the old value was retired, when, and by what. Overwriting destroys the one thing
you will want later, which is the ability to answer "what did we believe on the 3rd, and
when did that stop being true." It also makes a correction indistinguishable from a routine
update.

**A correction has to survive a rebuild.** This is the test almost nothing passes. If the
system regenerates a report, a summary, or a derived record, does last month's correction
still apply, or does the rebuild quietly restore the original error? A correction that does
not survive regeneration is one you will make again, and again, and eventually stop
trusting yourself about.

**Retention is a decision, not a default.** Decide how long the decision record lives, write
it down, and make sure it outlives the shortest applicable obligation. Discovering your
retention window during an inquiry is discovering it too late.

## 4 · What the audit trail has to survive

Four things. Most trails survive one or two.

- **A model change.** You will switch models. Does the record still make sense, and can you
  tell which decisions were made under which one?
- **A rebuild.** See above. This is the one that fails.
- **Staff turnover.** The person who knows why the exception exists will leave. If the
  reason lives in their head or in a chat thread, it is already gone.
- **An adversarial reading.** Someone who believes you did something wrong will read this
  trail looking for the gap. Read it that way yourself first.

---

## The self-assessment

Score honestly. The value is in the noes.

| # | Question | Yes / No |
|---|---|---|
| 1 | Can you produce, for one specific agent action last month, the records it read and the rules in force at that moment? | |
| 2 | Does your system log refusals, not only completed actions? | |
| 3 | Can you distinguish "checked and false" from "could not check" in your stored results? | |
| 4 | Is there any category of action your agent is technically capable of but mechanically prevented from taking? | |
| 5 | Are the rules that protect against invisible failures enforced by the system, or written in a document? | |
| 6 | Can an agent in your system mark its own work verified? | |
| 7 | When you corrected something the agent got wrong, is there a durable record showing the old value retired? | |
| 8 | Would that correction survive the system regenerating the artifact it lives in? | |
| 9 | Is your retention period for agent decision records written down anywhere? | |
| 10 | Does your audit trail contain sensitive payload data it does not need? (A yes here is a no.) | |

**Seven or more the right way:** you are in good shape, keep going. **Four to six:** normal,
and the gaps are probably in questions 6 through 8, which is the correction layer. **Three
or fewer:** you have a legible system that cannot yet tell you when it was wrong, which is a
specific and fixable condition rather than a general failing.

Deployments that score well on 1 through 5 usually score badly on 6 through 8. That is not a
coincidence. Logging is a build task with a clear finish line. Correction is a process
property with no natural moment where anyone notices it is missing.

## Where the runnable pieces are

Nothing here requires this repo, and nothing here is for sale. If you want working versions
of the mechanisms rather than the argument:

- Refusal and oracle-gated verification: `templates/ledger-tools/memory_engine.py`, which
  records `asserted` on write and will not promote to `verified` without a named check.
- Dated supersession and correction records: `templates/CONCLUSIONS_TEMPLATE.md` and the
  same engine's tombstone handling.
- Enforcement rather than instruction: `ci-kit/guards/`, where each guard ships with
  must-fail and must-pass fixtures so you can see it actually bites.
- The retrieval side, if the problem is that nobody can find what was decided:
  `templates/memory-desk/`.

## The regulatory context, and one date most sources get wrong

Checked against primary sources on 2026-08-19. Re-check before relying on any of it; the
first item moved less than a month before this was written, which is the whole reason it is
called out.

**EU AI Act, education.** Annex III point 3 of Regulation (EU) 2024/1689 classifies as
high-risk any AI used to determine admission, evaluate learning outcomes, assess the
appropriate level of education, or monitor students during tests. High-risk status carries
record-keeping, human oversight, and transparency obligations.

The date is the part to get right. Those Annex III obligations were originally set to apply
from 2 August 2026. **They now apply from 2 December 2027**, moved by the Digital Omnibus on
AI, Regulation (EU) 2026/1744, published 24 July 2026 and in force since 27 July. Anything
written before late July still says August 2026. A separate August 2027 figure that
circulates belongs to Annex I embedded-product systems rather than education, and the same
Omnibus moved that one to 2 August 2028.

**Logging duty and retention duty are different articles.** Article 12 requires that
high-risk systems "technically allow for the automatic recording of events ('logs') over the
lifetime of the system." That is a provider obligation and it sets no retention period. The
"at least six months" figure belongs to **Article 26(6)**, a deployer obligation to keep the
logs "for a period appropriate to the intended purpose of the high-risk AI system, of at
least six months." A document citing Article 12 for a six-month retention floor has
conflated the two.

**US federal procurement.** OMB M-25-21 and M-25-22 impose audit-trail, human-override, and
decision-logging requirements for high-impact AI, and are unaffected by the EU amendment.

The practical read: the regulatory clock is longer than most commentary suggests and the
procurement clock is not. Build for the audit you will face, not for the date.

## What this does not cover

Named so nobody assumes coverage that is not here.

- **Model selection, evaluation, and accuracy benchmarking.** Different problem, well
  covered elsewhere.
- **Bias and fairness assessment.** Genuinely important, genuinely a different discipline,
  and this does not substitute for it.
- **Interpreting which regulation applies to you.** This framework supports an audit. It
  does not tell you what you are subject to. Get that from counsel.
- **Security of the agent itself.** Prompt injection, credential handling, and the rest of
  the application security surface are a separate review.
