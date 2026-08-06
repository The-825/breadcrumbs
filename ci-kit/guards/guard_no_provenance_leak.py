#!/usr/bin/env python3
"""Guard: a public repo's commit history should not narrate its private origin.

When a public repo is extracted and generalized from private work, the code and
docs usually get reviewed for leaks. The commit messages and PR bodies usually
do not, and they are just as public and far more revealing, because they are
where people explain themselves. "Removed the client-specific example," "scrubbed
the employer detail," "generalized from our internal system" are all sentences
somebody writes without thinking, and each one tells a reader exactly what to go
looking for in the history.

This screens text before it becomes public. Point it at a commit message, a PR
body, or a range of commits.

THE DESIGN CONSTRAINT THAT SHAPES EVERYTHING HERE:

The forbidden terms cannot ship in this file. A public guard containing the
literal list of names you are trying to keep out of public view is a leak with
extra steps, and it is the exact mistake it exists to prevent. So the mechanism
is public and the wordlist is local: the terms live in a file you keep out of
version control, and the repo ships only a placeholder example.

That split is the point, and it generalizes past this one guard. Ship the check,
keep the sensitive parameter out of the artifact.

Usage:
    python3 guard_no_provenance_leak.py --terms .provenance-terms --text "message"
    python3 guard_no_provenance_leak.py --terms .provenance-terms --range origin/main..HEAD
    git log --format=%B -1 | python3 guard_no_provenance_leak.py --terms .provenance-terms --stdin

Tests live with the other guards, in tests/test_provenance_leak.py.

Terms file: one entry per line, blank lines and # comments ignored. Each entry is
matched case-insensitively as a whole word. Add it to .gitignore.

Exit 1 on any hit.
"""

import argparse
import re
import subprocess
import sys

# Phrases that narrate a scrub regardless of what the private thing was called.
# These are safe to ship because they name the ACT, not the subject, and the act
# is the tell: a reader who sees "de-identified" knows there was something to
# de-identify, even without knowing what.
ACT_PATTERNS = [
    r"\bde-?identif(y|ied|ication)\b",
    r"\bscrub(bed|bing)?\b",
    r"\banonymiz(e|ed|ation)\b",
    r"\bredact(ed|ion)?\b",
    r"\bsanitiz(e|ed)\b",
    r"\bremoved? (the )?(client|customer|employer|company|internal|proprietary)\b",
    r"\bgeneraliz(e|ed) from\b",
    r"\bextracted from (our|the) (internal|private|real|production) \w+\b",
    r"\bstripped? (out )?(the )?(names?|identif\w+|company|employer)\b",
    r"\bprivate repo\b",
    r"\binternal repo\b",
]


def load_terms(path):
    """Local, gitignored wordlist. Missing file is an error, not a pass."""
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#", 1)[0].strip()
            if line:
                out.append(line)
    return out


def scan(text, terms):
    """Returns a list of (kind, matched) findings."""
    hits = []
    for pat in ACT_PATTERNS:
        for m in re.finditer(pat, text, re.I):
            hits.append(("scrub-narration", m.group(0)))
    for term in terms:
        for m in re.finditer(rf"\b{re.escape(term)}\b", text, re.I):
            hits.append(("private-term", m.group(0)))
    return hits


def report(hits, where):
    if not hits:
        print(f"guard_no_provenance_leak: clean ({where})")
        return 0
    print(f"guard_no_provenance_leak: {len(hits)} finding(s) in {where}\n")
    for kind, matched in hits:
        if kind == "private-term":
            print(f"  private term {matched!r}. It must not appear in public text.")
        else:
            print(
                f"  narrates a scrub: {matched!r}. Say what the artifact IS now, "
                f"not what it was cleaned of."
            )
    print("\nRule: silent about provenance, plain about the artifact.")
    print("'Fixed the guard's false positives' is fine. 'Removed the employer")
    print("example' is not. The first describes the code; the second describes")
    print("the history you did not intend to publish.")
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--terms", help="local wordlist, keep it out of version control")
    ap.add_argument("--text")
    ap.add_argument("--range", dest="rng")
    ap.add_argument("--stdin", action="store_true")
    a = ap.parse_args()

    terms = load_terms(a.terms) if a.terms else []
    if not terms:
        print("warning: no terms file supplied, only scrub-narration patterns run.")

    if a.stdin:
        return report(scan(sys.stdin.read(), terms), "<stdin>")
    if a.text:
        return report(scan(a.text, terms), "<text>")
    if a.rng:
        body = subprocess.run(
            ["git", "log", "--format=%B", a.rng],
            capture_output=True, text=True, check=False,
        ).stdout
        return report(scan(body, terms), a.rng)

    ap.error("one of --text, --range, or --stdin is required")


if __name__ == "__main__":
    sys.exit(main())
