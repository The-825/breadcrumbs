# The chorus: freeze the facts a miss would make dangerous

Most of a rules file is reference, and reference is allowed to move. Slimming passes
relocate mechanics to satellite docs, reword sections for brevity, and replace
restatements with lookups. That is correct maintenance, and it has one dangerous edge
case: the handful of facts where a miss produces a wrong answer or an unsafe write. For
those, a lookup that sometimes does not happen is not a safeguard. They have to sit in
front of every session, every turn, in identical words.

That is the chorus: a short block at the very top of the rules file, frozen and
verbatim, enforced by a unit test that fails CI when a line goes missing or gets
paraphrased.

## Why verbatim, not just present

Song recall works on fixed form: every repetition reinforces the identical sequence,
and rewording a chorus breaks the automaticity. The same holds here. A fact that gets
paraphrased on each doc pass is a fact whose nuance eventually drops out. "The floor is
0.745" survives a paraphrase; "0.745, not 0.75, so a value rounding to 0.75 still
qualifies" is exactly the kind of clause a well-meaning rewrite compresses away, and the
compressed version produces confident wrong answers. So the chorus facts are phrased
identically every session and are never reworded during a slimming pass. Everything
below the chorus is reference, and reference stays free to move.

## What qualifies

The admission test is cost, not importance: what does a miss cost? A fact belongs in
the chorus only when a session that does not hold it will produce a wrong number or an
unsafe write before anything catches it. Typical residents: the one correct filter for
a core population, a threshold whose spoken version differs from the enforced version,
the non-negotiable query and auth rules, the merge discipline. Keep the block small; a
chorus that grows into a verse stops being automatic. If the block passes a dozen
facts, something in it belongs in reference instead.

## A generic worked example

Invented facts, placeholder values, to show the shape. At the top of the rules file:

```markdown
## THE CHORUS: frozen, verbatim, every session

Three facts where a miss produces a wrong answer or an unsafe write.
`tests/test_chorus.py` fails if any line goes missing or gets reworded.
Everything else in this file is reference, and reference is allowed to move.

1. **Open records** are `COALESCE(stage,'') NOT IN ('closed','expired')`.
   Never `stage = 'open'`; no such literal exists, and it silently drops
   the null-stage majority.
2. **The discount floor is 0.745, not 0.75**, so a value rounding to 0.75
   still qualifies. The spoken policy figure is still "0.75".
3. **All queries are parameterized.** Never an f-string with user input.
```

Fact 1 is the status-filter class: the intuitive predicate is wrong in a way no error
message reveals. Fact 2 is the rounding-threshold class: the enforced number and the
spoken number differ on purpose, and a paraphrase merges them. Fact 3 is a floor rule
that also has a mechanical guard; it earns a chorus line anyway because the guard fires
after the mistake and the chorus prevents it.

## The test that makes "frozen" real

A frozen block with no enforcement is a request. The test asserts on substrings, not
whole lines, so surrounding prose can still be edited; what cannot change is the fact
itself, in the words it is stated in. When a fact legitimately changes, the same PR
changes it in both places, which is exactly the deliberation intended.

```python
"""The chorus stays frozen and verbatim in the rules file."""
import re
import unittest
from pathlib import Path

RULES = Path(__file__).resolve().parents[1] / "CLAUDE.md"
CHORUS = [  # (label, substrings that must appear verbatim)
    ("open filter", ["COALESCE(stage,'') NOT IN ('closed','expired')"]),
    ("discount floor", ["0.745, not 0.75"]),
    ("parameterized queries", ["Never an f-string with user input"]),
]

class TestChorus(unittest.TestCase):
    def test_facts_verbatim(self):
        text = RULES.read_text(encoding="utf-8")
        block = re.search(r"^## THE CHORUS.*?(?=^## )", text, re.M | re.S)
        self.assertTrue(block, "rules file must open with the chorus block")
        for label, needles in CHORUS:
            for needle in needles:
                self.assertIn(needle, block.group(0),
                              f"{label}: chorus fact missing or reworded")

if __name__ == "__main__":
    unittest.main()
```

Apply the kit's guard discipline to it: prove the test bites before trusting it.
Reword one fact locally, watch the test fail, revert. A chorus test that never fails is
worse than none, because it certifies a freeze it does not enforce. Two cheap
companions are worth adding once the pattern settles: a size cap (assert the block
stays under a fixed line count, so the chorus cannot quietly grow into a verse) and a
count check (if the block claims "three facts," assert three numbered items, so the
file never lies to the sessions that read it).

The [rules spine](rules-spine.md) routes every rule to the cheapest mechanism that can
hold it: guards, the merge gate, the ledgers, and operator judgment for the rest. The
chorus test is the missing last rung of that enforcement story: the mechanism that
holds the rules file itself.
