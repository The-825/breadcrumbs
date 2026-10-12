# UI delivery evidence

Assumes a web interface you can run, a stated design direction, and access to its source revision. This kit ships a copy-and-adapt review worksheet. It does not automate browser checks or block a release. Review time depends on the interface and its journeys.

A green build can still leave a dead button, inaccessible form or unsupported status claim. Before delivery, verify the controls and states your user depends on and record what actually happened.

## Run the review

1. Record the exact source revision, target environment, reviewer and journey. Use public or synthetic examples.
2. Write the expected result before interacting. Mark missing requirements unresolved instead of inventing behavior.
3. Run the journey and inspect its result. Exercise keyboard navigation, relevant viewport sizes, and empty, loading and error states.
4. Connect factual claims and status labels to current evidence. A configured mode does not prove a live observation.
5. Compare edited copy with its source. Check actor, negation, scope, attribution and uncertainty. Natural wording cannot reverse the meaning.
6. Record pass, fail or unverified for each required check. Missing evidence is unverified. Fix failures and repeat affected checks against the new revision.

## Evidence worksheet

Revision:
Environment:
Reviewer:
Journey:
Design direction:

| Check | Expected result | Observed result | Evidence | Verdict |
|---|---|---|---|---|
| Main action and important secondary controls | Result visibly occurs | Pending | Pending | Unverified |
| Keyboard and focus | Relevant controls work without a mouse; focus remains visible | Pending | Pending | Unverified |
| Responsive layout | Content and controls remain usable at required viewport sizes | Pending | Pending | Unverified |
| Empty, loading and error states | State is honest and gives a useful next action | Pending | Pending | Unverified |
| Status and factual claims | Current evidence supports the label and claim | Pending | Pending | Unverified |
| Copy meaning | Actor, negation, scope, attribution and uncertainty are preserved | Pending | Pending | Unverified |

Use evidence references that another reviewer can open in the owning environment. Do not put credentials or user records in screenshots. A screenshot can show a state, but it cannot prove an unrecorded interaction occurred. Separate source inspection, executed checks and live observations.

## Compare the worksheet with your current review

Use one frozen synthetic page with a working control, a dead control, an unsupported live badge and a missing keyboard focus state. Run your current review and this worksheet on that same revision. Record defects caught, false positives and reviewer time. Unknown time stays unknown. This exercise measures the review method; it does not establish product quality.

Keep valid branded choices distinct from functional defects. Record omitted journeys and states. A passed subset does not establish full interface coverage or grant release authority.

## Source and refinement

The delivery-evidence pattern is informed by [anti-slop's core skill](https://github.com/miqdadbadjuber/anti-slop/blob/388cbe3b6c37d5175b9f460015bb092ef9e34894/skills/antislop/SKILL.md), MIT, especially its interaction, accessibility and factual-claim checks. This worksheet is written independently. It separates observed evidence from unverified checks and adds copy-meaning and coverage limits. It does not adopt the source's visual preferences or installation instructions.

For the wider after-change review, use [continuity sweep](continuity-sweep.md).
