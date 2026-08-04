#!/usr/bin/env python3
"""task_shape.py: classify a prompt's task shape and print at most ONE
line recommending a model tier. Called by model-routing-prompt-hook.sh
with the raw prompt on stdin (the hook does the jq extract).

Mirror of the routing table in templates/commands/model-check.md and
docs/model-playbook.md; change the table first, then this mirror. Fill
the TIERS values with your provider's current models; the placeholders
are deliberate.

  LOOKUP  -> the fast, cheap tier   (lookups, mechanical edits)
  SHIP    -> the daily-driver tier  (single-file features, standard debug)
  COMPLEX -> the deepest tier       (multi-system, architectural, audits)
  TRIVIAL -> no output at all: continuation replies ("yes", "go") must
             not get noise-tagged, or the hook becomes a per-turn tax.

Fail-open by construction: any error prints nothing and exits 0.
"""
import re
import sys

TIERS = {
    "LOOKUP": "<fast-model>",
    "SHIP": "<default-model>",
    "COMPLEX": "<deep-model>",
}

LOOKUP_RE = re.compile(
    r"\b(where is|show me|find the|read the|look up|grep|count|list files?|"
    r"what is the value|what's the value|which file)\b", re.I)
SHIP_RE = re.compile(
    r"\b(add|implement|extend|wire up|ship|create|fix|rename|write a test|"
    r"update the|bump)\b", re.I)
COMPLEX_RE = re.compile(
    r"\b(refactor|audit|debug|trace|why does|why is|design|review|"
    r"architect|investigate|migrate|optimi[sz]e|across|every file|"
    r"orchestrate|fan[- ]?out)\b", re.I)
CONTINUATION_RE = re.compile(
    r"^\s*(yes|no|go|ok(ay)?|ship it|do it|proceed|continue|thanks?|lgtm)\b[.!]?\s*$",
    re.I)


def classify(prompt: str) -> str:
    words = len(prompt.split())
    if CONTINUATION_RE.match(prompt) or words < 4:
        return "TRIVIAL"
    if COMPLEX_RE.search(prompt) or words > 150:
        return "COMPLEX"
    if LOOKUP_RE.search(prompt) and words <= 30:
        return "LOOKUP"
    if SHIP_RE.search(prompt):
        return "SHIP"
    return "TRIVIAL"  # illegible shape: stay silent rather than guess loudly


def main() -> int:
    try:
        prompt = sys.stdin.read()
    except Exception:
        return 0
    shape = classify(prompt or "")
    if shape == "TRIVIAL":
        return 0
    print(f"[model-routing] task shape {shape}: consider {TIERS[shape]} "
          "(table: docs/model-playbook.md; override freely, this is a hint)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
