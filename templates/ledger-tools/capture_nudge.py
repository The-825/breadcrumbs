#!/usr/bin/env python3
"""UserPromptSubmit hook: decision-capture nudge.

Scans the submitted prompt for ruling-shaped language (the decision-capture
rule: a ruling gets appended to the decisions ledger or conclusions store the
same turn it lands). On a match, prints a short reminder to stdout; on a
UserPromptSubmit hook, the harness adds hook stdout to the turn's context, so
the reminder lands next to the ruling it is about. No match: prints nothing,
so ordinary prompts stay noise-free.

Registration snippet and limits: capture-nudge.md next to this script.

Fail-open by design: always exits 0, stdlib only, no file or network I/O,
well under 100ms. A broken hook must never block a prompt.
"""
import json
import re
import sys

# Conservative ruling-shaped markers. Prefer a miss over noise: the nudge is
# only a reminder, but it lands on every matching prompt. Extend with the
# phrasings your operator actually uses.
PATTERNS = [
    re.compile(r"\bruling\b", re.IGNORECASE),
    re.compile(r"\bstanding rule\b", re.IGNORECASE),
    re.compile(r"\bfrom now on\b", re.IGNORECASE),
    re.compile(r"\bgoing forward\b", re.IGNORECASE),
    re.compile(r"\bverbatim\b", re.IGNORECASE),
    re.compile(r"\brule:", re.IGNORECASE),
    # Clause-initial "always <verb>" / "never <verb>": start of the prompt, a
    # new line, or right after sentence-ending punctuation. "never mind" is
    # excluded as a stock phrase.
    re.compile(
        r"(?:^|[.!?;:]\s+)(?:always|never)\s+(?!mind\b)[a-z]{2,}",
        re.IGNORECASE | re.MULTILINE,
    ),
]

# Edit the two file names to match your repo's ledger paths.
NUDGE = (
    "[capture-nudge] This prompt looks like it contains a ruling or standing "
    "instruction. Per the decision-capture rule, record it THIS turn, before "
    "moving on to the work it unblocks: operator rulings go to DECISIONS.md, "
    "verified facts to CONCLUSIONS.jsonl."
)


def main():
    try:
        raw = sys.stdin.read()
        if not raw:
            return 0
        try:
            payload = json.loads(raw)
        except ValueError:
            return 0
        if not isinstance(payload, dict):
            return 0
        prompt = payload.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            return 0
        if any(p.search(prompt) for p in PATTERNS):
            print(NUDGE)
    except Exception:
        # Fail-open: a hook error must never block or delay the prompt.
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
