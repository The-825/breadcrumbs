---
description: Triage a pasted meeting transcript. Extract the other party's questions and commitments, answer them grounded in live code and data (the code is the truth, docs may over-promise), convert their asks into the work plan, and treat committed dates as real deadlines.
argument-hint: "[who the meeting was with / context, if not obvious from the paste]"
---

Triage the pasted meeting transcript. Context, if given: **$ARGUMENTS**.

A raw transcript plus one line from the operator ("review this conversation and answer their questions") delegates the whole arc below. Do not ask for a spec. The binding blocks in your shared agent preamble apply (see `templates/AGENT_PREAMBLE_TEMPLATE.md` in the companion repo, or your repo's installed copy).

## Step 1: Extract the other party's queue

Read the transcript once and pull out, attributed to the right speaker:

1. **Questions** the other party asked (answered poorly, deferred, or unanswered in the meeting).
2. **Asks**: anything they requested, expected, or assumed the operator's side would do.
3. **Commitments the operator made**: deliverables, follow-ups, and especially **dates** ("by Wednesday" is a real, externally visible deadline, not color).
4. **Facts stated by either side** that touch the data model or operating policy. Operational facts dropped in passing often exist nowhere else and can change how the system should model reality; they are capture candidates for Step 5.

Voice-transcription artifacts get silent phonetic translation into your domain's real vocabulary (product names, table names, file formats); never treat a phonetic form as a new entity.

## Step 2: Answer grounded in live code and data

**The code is the truth to report; docs may over-promise.** For every question:

- System behavior: read the actual route, component, or job, not the design doc or README claim.
- Figures: find the canonical endpoint or report that already computes the number and mirror its query read-only. Never hand-roll a fresh aggregate; hand-rolled counts silently diverge from what the other party already sees.
- If a doc and the code disagree, answer from the code and note the doc drift as a follow-up.
- If something cannot be verified this session, say so explicitly rather than answering from doc wording. An unverified claim to a colleague is how wrong commitments happen.

## Step 3: Convert asks into the work plan

Their asks are the new priority queue. Build a board: each ask with a disposition (do-now / needs the operator's call / another team's turf / parked-with-pointer) and, for do-now items, the concrete next step. Turf items become questions for the owning person, never unilateral decisions. Committed dates order the queue.

## Step 4: Deliver

Answers first (each question, answered plainly, with its source: file, endpoint, live figure), then the board with running counts. The agent drafts, the operator delivers: produce the paste-ready reply or talking points and stop; never post to the operator's delivery channels (email, chat, external systems). Regulated PII stays out of anything durable; keep sensitive detail in-thread and scrubbed.

## Step 5: Capture

Same-turn capture to your conclusions store for any ruling or domain fact the transcript surfaced. If a committed date needs a future nudge, offer to set a scheduled reminder (if your harness supports one) rather than trusting session memory.
