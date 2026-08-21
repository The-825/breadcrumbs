# Breadcrumb Score

Capability lists fail at delegation because a declaration does not tell you what was
tested, when the evidence was observed, or how the system behaves when it is wrong.
Breadcrumb Score turns an owner-approved evidence set into a reproducible readiness
summary without treating missing evidence as a failed capability.

**Assumes:** Python 3.9 or newer and an assessment JSON file prepared from public or
explicitly permitted evidence.

**Ships:** yes. `breadcrumb_score.py`, the schema, the example, and the tests are a
copyable standard-library reference implementation. It does not collect repository
evidence or publish assessments for you.

## What the score means

Eight dimensions cover discovery, capability evidence, continuity, provenance,
correction, delegation, approvals, and outcome reliability. A dimension is scored from
1 to 5 only when it cites evidence. Unknown dimensions stay unscored and reduce evidence
coverage. They never become zeroes.

The tool withholds an overall score until at least five dimensions carry evidence. A
public-ready assessment also requires owner opt-in, human review, and a specific
publication approval record.

This is an evidence-scoped readiness assessment. It is not a security audit, compliance
certification, endorsement, or guarantee.

## Run it

```bash
python3 breadcrumb_score.py example-assessment.json
python3 -m unittest discover -s tests
```

The output includes:

- evidence coverage
- number of tested dimensions
- weighted score when coverage is sufficient
- readiness band
- individual dimension scores
- a deterministic digest of the complete assessment

## Score anchors

| Score | Meaning |
|---:|---|
| 1 | The function is materially absent. |
| 2 | It is declared but not demonstrated. |
| 3 | It works in a bounded example with meaningful gaps. |
| 4 | It is tested, traceable, correctable, and bounded. |
| 5 | Multiple representative tests and failure cases independently support it. |

## Publication boundary

Keep the assessment in `draft` while evidence is being assembled. Use
`owner_reviewed` only after a person has checked the target, scope, citations, scores,
and limitations. Use `published` only with a specific approval record. A later correction
creates a new assessment rather than rewriting the old digest.

Payment must never change a score. A paid review may expand evidence and testing depth,
but the same anchors and refusal rules still apply.

## Adaptation seam

The reference implementation validates an already assembled assessment. A production
collector should remain separate, because repository access, secrets, rate limits, and
owner consent are deployment-specific. Feed only normalized evidence records into this
calculator, and keep collection permissions outside the score.

