#!/usr/bin/env python3
"""Retrieval exam for a conclusions ledger: does any of it actually surface.

A staleness auditor (conclusions_audit.py, next to this script) asks whether
your entries are still TRUE. This asks the question nobody runs: whether they
can ever be SEEN. Those fail differently. A stale entry is wrong and gets
caught the moment somebody reads it. An unreachable entry is correct, well
written, and silently absent from every session that needed it, so nothing
ever prompts anyone to look. See docs/memory-measurement.md for the reasoning.

THREE PARTS, because there are three distinct failure modes and a single
overall score hides two of them.

  PART 1  REACHABILITY.  Per entry, against the real repo tree: could this
          ever surface? Four verdicts.

            precise      key is a file that exists. A session touching it
                         surfaces the entry.
            broad        key resolves to a directory or matches many files.
                         It fires, but it competes with everything else under
                         the same key and loses a capped lane most days.
            special      key is one of the declared special words your
                         matcher handles by name.
            unreachable  key is neither a path in the tree nor a special
                         word. It cannot fire. This is the finding.

  PART 2  LANE PROBE.  Reachability scores the corpus and says nothing about
          the lane. Simulates several different session-start conditions,
          computes what each would inject under your rank and cap, and diffs
          them. Identical output across genuinely different inputs means the
          lane is stuck: a corpus can score almost perfectly healthy while
          every session receives the same handful of entries.

  PART 3  USE READOUT.  Of the entries that DO win the lane, how many has any
          session ever acted on (schema fields `last_used` / `use_count`).
          An entry injected on every probe and used never is dead weight
          charging rent on every session.

THE MATCHER PROBLEM, and how this handles it honestly. Your boot matcher is
yours; this script cannot read your hook. What it ships is a MODEL of the
common shape (entries keyed by repo path, a cap on how many are injected, most
specific and most recent win) that you correct with --matcher. If your real
matcher diverges from the model, the numbers describe the model and not your
system, which is worse than no numbers. Read the config, set it to match, and
if it cannot express your matcher, say so in your own copy rather than
trusting the default.

RATCHET IT. --baseline writes or compares a small JSON of the counts, and
--fail-on-regression turns a worsening reachability score into a nonzero exit
so CI holds the line. Without the ratchet you get one good cleanup followed by
slow regrowth, which is how the corpus got here.

Usage:
  python3 retrieval_exam.py <ledger.jsonl> --root <repo>
  ... --matcher <config.json>        # correct the matcher model (see below)
  ... --probes <probes.json>         # session-start conditions to simulate
  ... --baseline <baseline.json>     # compare against a stored baseline
  ... --write-baseline <path>        # write the current counts as a baseline
  ... --fail-on-regression           # exit 1 when reachability got worse
  ... --json                         # machine-readable output
  ... --selftest                     # run offline fixture tests and exit

Matcher config, all keys optional:
  {"special_paths": ["domain", "operations", "process"],
   "injection_cap": 6,
   "recency_field": "verified",
   "broad_fanout": 8}

Probes file: [{"name": "backend session", "touched": ["src/app.py"]}, ...].
With no probes file the script derives one probe per top-level directory that
contains files, which makes it runnable against any repo on the first try.

Stdlib only. Exit 0 on a completed exam regardless of findings, EXCEPT under
--fail-on-regression; nonzero when the ledger cannot be read or a selftest
check fails.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import sys
import tempfile

DEFAULT_SPECIAL_PATHS = ["domain", "operations", "process"]
# How many entries the boot lane injects per session. The single most
# important number here: it is what turns "reachable" into "actually seen",
# and it is almost always smaller than people remember.
DEFAULT_INJECTION_CAP = 6
# A key matching more than this many files is broad rather than precise. It
# fires constantly, so it wins the lane on traffic rather than on relevance.
DEFAULT_BROAD_FANOUT = 8
DEFAULT_RECENCY_FIELD = "verified"

PRECISE = "precise"
BROAD = "broad"
SPECIAL = "special"
UNREACHABLE = "unreachable"
VERDICTS = (PRECISE, BROAD, SPECIAL, UNREACHABLE)


class Matcher:
    """The model of your boot matcher. Correct it with --matcher."""

    def __init__(self, config=None):
        cfg = config or {}
        self.special_paths = set(cfg.get("special_paths", DEFAULT_SPECIAL_PATHS))
        self.injection_cap = int(cfg.get("injection_cap", DEFAULT_INJECTION_CAP))
        self.broad_fanout = int(cfg.get("broad_fanout", DEFAULT_BROAD_FANOUT))
        self.recency_field = cfg.get("recency_field", DEFAULT_RECENCY_FIELD)


def _parse_date(value):
    try:
        return dt.date.fromisoformat((value or "").strip())
    except (AttributeError, TypeError, ValueError):
        return None


def _entry_date(entry, matcher):
    return (
        _parse_date(entry.get(matcher.recency_field))
        or _parse_date(entry.get("when"))
        or dt.date.min
    )


def list_tree(root):
    """Every file path in the repo, relative and posix-style.

    Skips .git and common vendored directories; those inflate fanout counts
    and no matcher keys entries into them.
    """
    skip = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist"}
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for name in filenames:
            full = os.path.join(dirpath, name)
            out.append(os.path.relpath(full, root).replace(os.sep, "/"))
    return sorted(out)


def matched_files(key, tree, root):
    """Which files in the tree this key would fire on."""
    if not key:
        return []
    if any(ch in key for ch in "*?["):
        return [p for p in tree if fnmatch.fnmatch(p, key)]
    norm = key.rstrip("/")
    if os.path.isdir(os.path.join(root, norm)):
        prefix = norm + "/"
        return [p for p in tree if p.startswith(prefix)]
    if norm in tree:
        return [norm]
    return []


def classify_reachability(entries, tree, root, matcher):
    """Assign a reachability verdict to every parsed entry."""
    results = []
    for line_no, entry in entries:
        key = (entry.get("path") or "").strip()
        hits = []
        if key in matcher.special_paths:
            verdict, note = SPECIAL, "special key, handled by name"
        else:
            hits = matched_files(key, tree, root)
            if not hits:
                verdict = UNREACHABLE
                note = (
                    "key is not a path in the tree and not a declared special "
                    "key; nothing can make this fire"
                )
            elif len(hits) > matcher.broad_fanout:
                verdict = BROAD
                note = f"matches {len(hits)} files, over the broad_fanout threshold"
            else:
                verdict = PRECISE
                note = f"matches {len(hits)} file(s)"
        results.append({
            "line_no": line_no,
            "entry": entry,
            "key": key,
            "verdict": verdict,
            "note": note,
            "hits": hits,
        })
    return results


def default_probes(tree):
    """One probe per top-level directory that holds files, plus a root probe.

    Derived so the exam runs against any repo with no configuration. Real
    probes should mirror the session shapes you actually run.
    """
    by_dir = {}
    for path in tree:
        head = path.split("/")[0] if "/" in path else "."
        by_dir.setdefault(head, path)
    return [
        {"name": f"session touching {head}", "touched": [sample]}
        for head, sample in sorted(by_dir.items())
    ]


def injected_for(probe, results, matcher):
    """What the lane would inject for one probe, after rank and cap.

    Rank: entries whose key fires on a touched path, most specific first
    (fewest matched files), then most recent, then earliest line for a stable
    order. Special-key entries are treated as always-eligible, which is what
    a matcher handling them by name does.
    """
    touched = set(probe.get("touched") or [])
    eligible = []
    for r in results:
        if r["verdict"] == UNREACHABLE:
            continue
        if r["verdict"] == SPECIAL or (touched & set(r["hits"])):
            eligible.append(r)
    eligible.sort(key=lambda r: (
        len(r["hits"]) if r["verdict"] != SPECIAL else 10**6,
        -_entry_date(r["entry"], matcher).toordinal(),
        r["line_no"],
    ))
    return eligible[: matcher.injection_cap]


def run_lane_probe(results, probes, matcher):
    """Simulate every probe and report whether the lane actually varies."""
    runs = []
    for probe in probes:
        injected = injected_for(probe, results, matcher)
        runs.append({
            "name": probe.get("name", "unnamed"),
            "line_nos": [r["line_no"] for r in injected],
        })
    signatures = {tuple(run["line_nos"]) for run in runs}
    always = set.intersection(
        *[set(run["line_nos"]) for run in runs]
    ) if runs else set()
    # A lane that only ever emits special-key entries is not evidence of a
    # stuck lane. It means the probes never touched a file any entry keys on,
    # which is a finding about the PROBES. Reporting that as "stuck" would be
    # the exam making the same mistake it exists to catch: a confident verdict
    # about a lane that was never exercised.
    by_line = {r["line_no"]: r for r in results}
    exercised = any(
        by_line[n]["verdict"] != SPECIAL
        for run in runs for n in run["line_nos"] if n in by_line
    )
    return {
        "runs": runs,
        "distinct_injections": len(signatures),
        "stuck": len(runs) > 1 and len(signatures) == 1 and exercised,
        "unexercised": bool(runs) and not exercised,
        "always_injected": sorted(always),
    }


def run_forbidden_check(results, probes, matcher):
    """A superseded value must not win retrieval.

    The failure this catches: an entry marked `obsoleted_by` still gets
    injected, so the model sees the OLD ruling this turn and answers from it
    with full confidence. Correction that stops at the ledger row and never
    reaches the retrieval lane is not correction; the descent has to complete.

    Verdicts, per the could-not-run-is-not-a-pass principle:
    - forbidden_hits: superseded entries injected on at least one probe, each
      named with the probe that surfaced it. These are real failures.
    - clean: reachable superseded entries exist and no probe injected one.
    - unexercised: superseded entries exist but none is reachable, so the
      lane was never in a position to make the mistake. Says nothing yet.
    """
    superseded = [r for r in results if r["entry"].get("obsoleted_by")]
    hits = []
    for r in superseded:
        for probe in probes:
            injected = injected_for(probe, results, matcher)
            if r["line_no"] in [i["line_no"] for i in injected]:
                hits.append({
                    "line_no": r["line_no"],
                    "key": r["key"],
                    "obsoleted_by": r["entry"]["obsoleted_by"],
                    "probe": probe.get("name", "unnamed"),
                })
                break
    reachable = [r for r in superseded if r["verdict"] != UNREACHABLE]
    return {
        "superseded": len(superseded),
        "forbidden_hits": hits,
        "unexercised": bool(superseded) and not reachable,
    }


def run_use_readout(results, probe_report, today, matcher):
    """Use stamps, read across the corpus rather than one entry at a time."""
    live = [r for r in results if r["verdict"] != UNREACHABLE]
    stamped = [r for r in live if r["entry"].get("use_count")]
    by_line = {r["line_no"]: r for r in results}
    dead_weight = []
    for line_no in probe_report.get("always_injected", []):
        r = by_line.get(line_no)
        if r and not r["entry"].get("use_count"):
            dead_weight.append(r)
    return {
        "live": len(live),
        "stamped": len(stamped),
        "never_stamped": len(live) - len(stamped),
        "dead_weight": dead_weight,
    }


def counts_from(results):
    counts = {v: 0 for v in VERDICTS}
    for r in results:
        counts[r["verdict"]] += 1
    return counts


def compare_baseline(counts, baseline):
    """Regression test. Reachability may improve, never decay.

    More unreachable entries is the regression. Fewer precise entries with the
    same total is the subtler one, since re-keying an entry to something broad
    reads as a cleanup and is a downgrade.
    """
    regressions = []
    old = baseline.get("counts", {})
    if counts[UNREACHABLE] > old.get(UNREACHABLE, 0):
        regressions.append(
            f"unreachable rose from {old.get(UNREACHABLE, 0)} to {counts[UNREACHABLE]}"
        )
    if counts[PRECISE] < old.get(PRECISE, 0):
        regressions.append(
            f"precise fell from {old.get(PRECISE, 0)} to {counts[PRECISE]}"
        )
    return regressions


def _short_what(entry, limit=100):
    what = (entry.get("what") or "").strip()
    return what if len(what) <= limit else what[: limit - 3] + "..."


def build_report(results, probe_report, use_report, counts, ledger_rel, today,
                 matcher, regressions, forbidden=None):
    lines = []
    lines.append(f"Retrieval exam ({today.isoformat()})")
    lines.append(
        f"Ledger: {ledger_rel}  entries={len(results)}  "
        f"injection_cap={matcher.injection_cap}"
    )
    lines.append("")
    lines.append("PART 1  REACHABILITY")
    lines.append(
        "  precise={precise}  broad={broad}  special={special}  "
        "unreachable={unreachable}".format(**counts)
    )
    unreachable = [r for r in results if r["verdict"] == UNREACHABLE]
    lines.append("")
    lines.append(f"  UNREACHABLE ({len(unreachable)})  [cannot fire; write-only]")
    if not unreachable:
        lines.append("    none")
    for r in unreachable:
        lines.append(f"    line {r['line_no']:>4}  key={r['key'] or '(empty)'}")
        lines.append(f"               {_short_what(r['entry'])}")
    broad = [r for r in results if r["verdict"] == BROAD]
    lines.append("")
    lines.append(f"  BROAD ({len(broad)})  [fires, rarely wins a capped lane]")
    if not broad:
        lines.append("    none")
    for r in broad:
        lines.append(f"    line {r['line_no']:>4}  key={r['key']}  [{r['note']}]")

    lines.append("")
    lines.append("PART 2  LANE PROBE")
    lines.append(
        f"  probes={len(probe_report['runs'])}  "
        f"distinct_injections={probe_report['distinct_injections']}"
    )
    if probe_report["stuck"]:
        lines.append(
            "  STUCK: every probe received an identical injection. The corpus "
            "score above is describing a lane that does not vary."
        )
    if probe_report.get("unexercised"):
        lines.append(
            "  UNEXERCISED: no probe touched a file any entry keys on, so only "
            "special-key entries were injected. Fix the probes before reading "
            "anything into this part; it says nothing about the lane yet."
        )
    if probe_report["always_injected"]:
        lines.append(
            "  Injected on every probe: lines "
            + ", ".join(str(n) for n in probe_report["always_injected"])
        )

    lines.append("")
    lines.append("PART 3  USE READOUT")
    lines.append(
        f"  live={use_report['live']}  stamped={use_report['stamped']}  "
        f"never_stamped={use_report['never_stamped']}"
    )
    if use_report["dead_weight"]:
        lines.append(
            f"  DEAD WEIGHT ({len(use_report['dead_weight'])})  "
            "[injected on every probe, never used]"
        )
        for r in use_report["dead_weight"]:
            lines.append(f"    line {r['line_no']:>4}  key={r['key']}")
            lines.append(f"               {_short_what(r['entry'])}")
    elif use_report["never_stamped"] == use_report["live"]:
        lines.append(
            "  No entry carries a use stamp. Either the stamping habit is not "
            "running or nothing is being used; the exam cannot tell which."
        )

    if forbidden is not None:
        lines.append("")
        lines.append("PART 4  FORBIDDEN HITS")
        lines.append(f"  superseded={forbidden['superseded']}  "
                     f"forbidden_hits={len(forbidden['forbidden_hits'])}")
        for hit in forbidden["forbidden_hits"]:
            lines.append(
                f"  FORBIDDEN: line {hit['line_no']} (key={hit['key']}) is "
                f"obsoleted_by {hit['obsoleted_by']} and still injected on "
                f"probe '{hit['probe']}'. The model sees the old ruling."
            )
        if forbidden["unexercised"]:
            lines.append(
                "  UNEXERCISED: superseded entries exist but none is "
                "reachable, so the lane never had the chance to surface one. "
                "Says nothing about the lane yet."
            )
        if (not forbidden["forbidden_hits"] and not forbidden["unexercised"]
                and forbidden["superseded"]):
            lines.append("  clean: no superseded entry won retrieval.")
        if not forbidden["superseded"]:
            lines.append("  no superseded entries in the ledger.")

    if regressions:
        lines.append("")
        lines.append("BASELINE REGRESSION")
        for reg in regressions:
            lines.append(f"  {reg}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# SURVEY MODE: the exam for a repo that has no ledger yet.
#
# Everything above needs a conclusions store in this kit's schema, which means
# it only runs for people who already adopted the pattern, who are exactly the
# people who need it least. Survey mode asks the same question of what a normal
# repo already has: a rules file and a pile of markdown.
#
# The mechanic is different because the lane is different. With no ledger there
# is no injection cap to model. What loads automatically is the rules file, and
# every other document is reachable only if something the agent already read
# points at it. So reachability here is link distance from the boot surface,
# and the finding is the orphan: a document nobody links, which a session will
# never open on its own no matter how good it is.
#
# LIMITS, stated because overclaiming here would be the exact failure this kit
# is about. This follows markdown links only. A file named in prose without a
# link is invisible to it, and an agent that greps can still find an orphan.
# "Orphan" means unsignposted, not unfindable. It is the difference between a
# document the environment offers and one a human has to remember exists.
# ---------------------------------------------------------------------------

# Files a session is handed automatically, by convention across harnesses.
# Order matters only for reporting; all of them are treated as boot surface.
BOOT_FILES = [
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    ".cursorrules",
    ".github/copilot-instructions.md",
    "README.md",
]
# Past this many hops from the boot surface, a document is not signposted in
# any practical sense: nothing short of a deliberate hunt reaches it.
DEEP_HOPS = 3

BOOTED = "booted"
LINKED = "linked"
DEEP = "deep"
ISLAND = "island"
ORPHAN = "orphan"
SURVEY_VERDICTS = (BOOTED, LINKED, DEEP, ISLAND, ORPHAN)

_LINK_RE = None


def _link_targets(text):
    """Relative markdown link targets in a document, external links dropped."""
    global _LINK_RE
    if _LINK_RE is None:
        import re
        _LINK_RE = re.compile(r"\]\(\s*([^)\s]+?)\s*(?:\s+\"[^\"]*\")?\)")
    out = []
    for raw in _LINK_RE.findall(text):
        if raw.startswith(("http://", "https://", "mailto:", "#")):
            continue
        out.append(raw.split("#", 1)[0].strip())

    return [t for t in out if t]


def _read_text(root, rel):
    try:
        with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def survey_repo(root, tree, deep_hops=DEEP_HOPS):
    """Classify every markdown document by link distance from the boot surface."""
    docs = [p for p in tree if p.lower().endswith(".md")]
    doc_set = set(docs)
    roots = [p for p in BOOT_FILES if p in doc_set]

    # Link graph over documents only. A link to a non-markdown file is a real
    # pointer but not a document that needs its own reachability verdict.
    edges, inbound = {}, {p: 0 for p in docs}
    for doc in docs:
        base = os.path.dirname(doc)
        targets = []
        for raw in _link_targets(_read_text(root, doc)):
            resolved = os.path.normpath(os.path.join(base, raw)).replace(os.sep, "/")
            # A link to a directory resolves to its README, because that is
            # what the forge renders and what a reader following the link
            # lands on. Skipping this would report a whole repo as orphaned
            # over a trailing slash, which is a dramatic finding and a wrong
            # one.
            if resolved not in doc_set:
                as_index = f"{resolved.rstrip('/')}/README.md"
                if as_index in doc_set:
                    resolved = as_index
            if resolved in doc_set and resolved != doc:
                targets.append(resolved)
        edges[doc] = sorted(set(targets))
        for t in edges[doc]:
            inbound[t] = inbound.get(t, 0) + 1

    depth = {r: 0 for r in roots}
    frontier = list(roots)
    while frontier:
        nxt = []
        for node in frontier:
            for t in edges.get(node, []):
                if t not in depth:
                    depth[t] = depth[node] + 1
                    nxt.append(t)
        frontier = nxt

    results = []
    for doc in docs:
        d = depth.get(doc)
        if doc in roots:
            verdict, note = BOOTED, "loaded automatically at session start"
        elif d is None and inbound.get(doc, 0) == 0:
            verdict, note = ORPHAN, "nothing links here; a session never opens it on its own"
        elif d is None:
            verdict, note = ISLAND, (
                f"linked only from documents that are themselves unreachable "
                f"({inbound.get(doc, 0)} inbound)"
            )
        elif d > deep_hops:
            verdict, note = DEEP, f"{d} hops from the boot surface"
        else:
            verdict, note = LINKED, f"{d} hop(s) from the boot surface"
        results.append({
            "path": doc,
            "verdict": verdict,
            "note": note,
            "depth": d,
            "inbound": inbound.get(doc, 0),
        })
    results.sort(key=lambda r: (SURVEY_VERDICTS.index(r["verdict"]), r["path"]))
    return {"results": results, "roots": roots, "docs": len(docs)}


def survey_counts(survey):
    counts = {v: 0 for v in SURVEY_VERDICTS}
    for r in survey["results"]:
        counts[r["verdict"]] += 1
    return counts


def boot_weight(root, roots):
    """What every session pays before doing any work."""
    total_bytes = total_lines = 0
    per_file = []
    for rel in roots:
        text = _read_text(root, rel)
        b, l = len(text.encode("utf-8")), len(text.splitlines())
        per_file.append({"path": rel, "bytes": b, "lines": l})
        total_bytes += b
        total_lines += l
    return {"per_file": per_file, "bytes": total_bytes, "lines": total_lines}


def build_survey_report(survey, counts, weight, root_label, today, deep_hops):
    r = survey["results"]
    lines = []
    lines.append(f"Retrieval exam, survey mode ({today.isoformat()})")
    lines.append(f"Repo: {root_label}  markdown documents={survey['docs']}")
    lines.append("")
    lines.append("BOOT SURFACE  [what every session is handed automatically]")
    if not survey["roots"]:
        lines.append(
            "  none found. No CLAUDE.md, AGENTS.md, or README.md at the root, so "
            "nothing in this repo reaches a session unless a human pastes it."
        )
    for f in weight["per_file"]:
        lines.append(f"  {f['path']}  {f['lines']} lines, {f['bytes']} bytes")
    if survey["roots"]:
        lines.append(
            f"  Every session pays {weight['lines']} lines / {weight['bytes']} bytes "
            "before any work happens."
        )
    lines.append("")
    lines.append("REACHABILITY  [link distance from the boot surface]")
    lines.append(
        "  booted={booted}  linked={linked}  deep={deep}  island={island}  "
        "orphan={orphan}".format(**counts)
    )

    for verdict, legend in (
        (ORPHAN, "nothing links here; unsignposted"),
        (ISLAND, "linked only from unreachable documents"),
        (DEEP, f"more than {deep_hops} hops out"),
    ):
        rows = [x for x in r if x["verdict"] == verdict]
        lines.append("")
        lines.append(f"  {verdict.upper()} ({len(rows)})  [{legend}]")
        if not rows:
            lines.append("    none")
        for x in rows:
            lines.append(f"    {x['path']}  [{x['note']}]")

    lines.append("")
    lines.append("WHAT THIS DOES NOT MEASURE")
    lines.append(
        "  Markdown links only. A file named in prose without a link reads as an "
        "orphan here, and an agent that greps can still find one. Orphan means "
        "unsignposted, not unfindable."
    )
    lines.append(
        "  Nothing about use. Whether a session acted on a document needs a "
        "conclusions store with use stamps; run the full exam once you have one."
    )
    return "\n".join(lines) + "\n"


def parse_ledger(lines):
    parsed, malformed = [], []
    for line_no, raw in enumerate(lines, start=1):
        raw = raw.strip()
        if not raw:
            continue
        try:
            entry = json.loads(raw)
        except ValueError:
            malformed.append((line_no, raw[:80]))
            continue
        if not isinstance(entry, dict):
            malformed.append((line_no, raw[:80]))
            continue
        parsed.append((line_no, entry))
    return parsed, malformed


def selftest():
    """Offline fixtures: every verdict, a stuck lane, a varying lane, dead
    weight, and both baseline regressions."""
    today = dt.date(2026, 8, 6)
    matcher = Matcher({"injection_cap": 2, "broad_fanout": 2})
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "src"))
        os.makedirs(os.path.join(tmp, "wide"))
        for name in ("a.py", "b.py"):
            with open(os.path.join(tmp, "src", name), "w", encoding="utf-8") as fh:
                fh.write("# fixture\n")
        for i in range(4):
            with open(os.path.join(tmp, "wide", f"f{i}.py"), "w", encoding="utf-8") as fh:
                fh.write("# fixture\n")
        tree = list_tree(tmp)
        fixtures = [
            json.dumps({"path": "src/a.py", "when": "2026-08-01",
                        "what": "Precise, keyed to a real file."}),
            json.dumps({"path": "wide", "when": "2026-08-01",
                        "what": "Broad, keyed to a directory of many files."}),
            json.dumps({"path": "domain", "when": "2026-08-01",
                        "what": "Special key handled by name."}),
            json.dumps({"path": "the orders table", "when": "2026-08-01",
                        "what": "Unreachable: a bare noun, not a path."}),
            json.dumps({"path": "src/b.py", "when": "2026-08-02",
                        "what": "Precise and used.", "use_count": 3,
                        "last_used": "2026-08-05"}),
            "{not valid json",
        ]
        parsed, malformed = parse_ledger(fixtures)
        results = classify_reachability(parsed, tree, tmp, matcher)
        counts = counts_from(results)

        varying = run_lane_probe(results, [
            {"name": "a", "touched": ["src/a.py"]},
            {"name": "b", "touched": ["src/b.py"]},
        ], matcher)
        # Two probes that touch nothing any precise entry keys on: both fall
        # back to the always-eligible special entry, so the lane is stuck.
        stuck = run_lane_probe(results, [
            {"name": "x", "touched": ["wide/f0.py"]},
            {"name": "y", "touched": ["wide/f1.py"]},
        ], Matcher({"injection_cap": 1, "broad_fanout": 2}))
        use = run_use_readout(results, stuck, today, matcher)

        checks = [
            ("precise verdict", results[0]["verdict"] == PRECISE),
            ("broad verdict", results[1]["verdict"] == BROAD),
            ("special verdict", results[2]["verdict"] == SPECIAL),
            ("unreachable verdict", results[3]["verdict"] == UNREACHABLE),
            ("malformed line counted", len(malformed) == 1),
            ("counts add up", sum(counts.values()) == len(results)),
            ("varying lane not flagged stuck", not varying["stuck"]),
            ("identical lane flagged stuck", stuck["stuck"]),
            # Probes touching a file no entry keys on. Only the special entry
            # is eligible, so the lane never varies but that says nothing
            # about the lane: unexercised, not stuck.
            ("specials-only lane flagged unexercised, not stuck",
             (lambda p: p["unexercised"] and not p["stuck"])(
                 run_lane_probe(results, [
                     {"name": "p", "touched": ["unkeyed.py"]},
                     {"name": "q", "touched": ["unkeyed.py"]},
                 ], matcher))),
            ("use stamps counted", use["stamped"] == 1),
            ("dead weight found", len(use["dead_weight"]) == 1),
            # Forbidden hits: a superseded entry keyed to a touched file wins
            # injection (failure); one keyed to an untouched file stays out
            # (clean); one that is unreachable cannot exercise the check.
            ("superseded entry that wins retrieval is a forbidden hit",
             (lambda f: len(f["forbidden_hits"]) == 1
              and f["forbidden_hits"][0]["obsoleted_by"] == "src/b.py@2026-08-02")(
                 run_forbidden_check(
                     classify_reachability(parse_ledger([json.dumps(
                         {"path": "src/a.py", "when": "2026-07-01",
                          "what": "Old ruling, superseded.",
                          "obsoleted_by": "src/b.py@2026-08-02"})])[0]
                         + parsed, tree, tmp, matcher),
                     [{"name": "a", "touched": ["src/a.py"]}], matcher))),
            ("superseded entry never injected is clean",
             (lambda f: not f["forbidden_hits"] and not f["unexercised"])(
                 run_forbidden_check(
                     classify_reachability(parse_ledger([json.dumps(
                         {"path": "src/a.py", "when": "2026-07-01",
                          "what": "Old ruling, superseded.",
                          "obsoleted_by": "src/b.py"})])[0] + parsed,
                         tree, tmp, matcher),
                     [{"name": "b", "touched": ["src/b.py"]}], matcher))),
            # The revert case: a value flips A -> B -> A. Both earlier entries
            # carry obsoleted_by; the final entry RESTATES the original value
            # as a new current entry. The check must inject the current entry
            # and flag neither the revert (current despite its old value) nor
            # report a hit when only the current entry wins the lane.
            ("a revert chain injects the current entry and reports no hit",
             (lambda rs, f: not f["forbidden_hits"] and not f["unexercised"]
              and [i["line_no"] for i in injected_for(
                  {"name": "a", "touched": ["src/a.py"]}, rs,
                  Matcher({"injection_cap": 1, "broad_fanout": 2}))]
              == [3])(
                 *(lambda rs: (rs, run_forbidden_check(
                     rs, [{"name": "a", "touched": ["src/a.py"]}],
                     Matcher({"injection_cap": 1, "broad_fanout": 2}))))(
                     classify_reachability(parse_ledger([
                         json.dumps({"path": "src/a.py", "when": "2026-07-01",
                                     "what": "value A",
                                     "obsoleted_by": "src/a.py@2026-07-10"}),
                         json.dumps({"path": "src/a.py", "when": "2026-07-10",
                                     "what": "value B",
                                     "obsoleted_by": "src/a.py@2026-07-20"}),
                         json.dumps({"path": "src/a.py", "when": "2026-07-20",
                                     "what": "value A, restated as current"}),
                     ])[0], tree, tmp, matcher)))),
            ("unreachable superseded entry reports unexercised, never clean",
             (lambda f: f["unexercised"] and not f["forbidden_hits"])(
                 run_forbidden_check(
                     classify_reachability(parse_ledger([json.dumps(
                         {"path": "a bare noun", "when": "2026-07-01",
                          "what": "Old ruling, superseded, unreachable.",
                          "obsoleted_by": "src/b.py"})])[0],
                         tree, tmp, matcher),
                     [{"name": "a", "touched": ["src/a.py"]}], matcher))),
            ("unreachable rise is a regression",
             bool(compare_baseline(counts, {"counts": {UNREACHABLE: 0, PRECISE: 2}}))),
            ("precise drop is a regression",
             bool(compare_baseline(counts, {"counts": {UNREACHABLE: 1, PRECISE: 5}}))),
            ("matching baseline is clean",
             not compare_baseline(counts, {"counts": counts})),
        ]
        # Survey mode fixtures: a boot file linking one doc, that doc linking
        # a deeper one, an unlinked orphan, and an island pair reachable only
        # from the orphan.
        os.makedirs(os.path.join(tmp, "docs"))
        files = {
            "CLAUDE.md": "rules. see [one](docs/one.md) and [ext](https://x.test)\n",
            "docs/one.md": "one. see [two](two.md)\n",
            "docs/two.md": "two. see [three](three.md)\n",
            "docs/three.md": "three, three hops out\n",
            "docs/orphan.md": "nobody links me. i link [island](island.md)\n",
            "docs/island.md": "linked, but only from an orphan\n",
        }
        for rel, body in files.items():
            with open(os.path.join(tmp, rel), "w", encoding="utf-8") as fh:
                fh.write(body)
        stree = list_tree(tmp)
        survey = survey_repo(tmp, stree, deep_hops=2)
        by_path = {r["path"]: r for r in survey["results"]}
        scounts = survey_counts(survey)
        weight = boot_weight(tmp, survey["roots"])

        checks += [
            ("boot file classified booted", by_path["CLAUDE.md"]["verdict"] == BOOTED),
            ("one hop classified linked", by_path["docs/one.md"]["verdict"] == LINKED),
            ("depth counted correctly", by_path["docs/two.md"]["depth"] == 2),
            ("past deep_hops classified deep", by_path["docs/three.md"]["verdict"] == DEEP),
            ("unlinked doc classified orphan", by_path["docs/orphan.md"]["verdict"] == ORPHAN),
            ("orphan-only inbound classified island",
             by_path["docs/island.md"]["verdict"] == ISLAND),
            ("external links ignored", by_path["CLAUDE.md"]["depth"] == 0),
            ("survey counts add up", sum(scounts.values()) == len(survey["results"])),
            ("boot weight measured", weight["bytes"] > 0 and weight["lines"] > 0),
        ]

        failed = [name for name, ok in checks if not ok]
        for name, ok in checks:
            print(f"  {'PASS' if ok else 'FAIL'}  {name}")
        if failed:
            print(f"selftest: {len(failed)} check(s) failed.")
            return 1
        print(f"selftest: all {len(checks)} checks passed.")
        return 0


def _load_json(path, label):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Retrieval exam for a conclusions jsonl ledger"
    )
    ap.add_argument("ledger", nargs="?", default="CONCLUSIONS.jsonl",
                    help="path to the ledger (default: CONCLUSIONS.jsonl)")
    ap.add_argument("--root", default=".", metavar="DIR",
                    help="repo root that entry keys resolve against")
    ap.add_argument("--matcher", metavar="PATH",
                    help="JSON config correcting the matcher model")
    ap.add_argument("--probes", metavar="PATH",
                    help="JSON list of session-start conditions to simulate")
    ap.add_argument("--baseline", metavar="PATH",
                    help="compare counts against a stored baseline")
    ap.add_argument("--write-baseline", metavar="PATH",
                    help="write the current counts as a baseline and exit 0")
    ap.add_argument("--fail-on-regression", action="store_true",
                    help="exit 1 when reachability got worse than --baseline")
    ap.add_argument("--fail-on-forbidden", action="store_true",
                    help="exit 1 when a superseded entry wins retrieval")
    ap.add_argument("--json", action="store_true", dest="as_json",
                    help="emit machine-readable output")
    ap.add_argument("--survey", action="store_true",
                    help="no-ledger mode: classify the repo's markdown by link "
                         "distance from the boot surface (see module header)")
    ap.add_argument("--deep-hops", type=int, default=DEEP_HOPS, metavar="N",
                    help=f"survey mode: hops past which a doc counts as deep "
                         f"(default: {DEEP_HOPS})")
    ap.add_argument("--selftest", action="store_true",
                    help="run offline fixture tests and exit")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if not os.path.isdir(args.root):
        print(f"ERROR: root is not a directory: {args.root}", file=sys.stderr)
        return 1

    if args.survey:
        today = dt.date.today()
        tree = list_tree(args.root)
        survey = survey_repo(args.root, tree, args.deep_hops)
        counts = survey_counts(survey)
        weight = boot_weight(args.root, survey["roots"])
        if args.write_baseline:
            with open(args.write_baseline, "w", encoding="utf-8") as fh:
                json.dump({"date": today.isoformat(), "mode": "survey",
                           "counts": counts}, fh, indent=2)
                fh.write("\n")
            print(f"Baseline written to {args.write_baseline}: {counts}")
            return 0
        regressions = []
        if args.baseline and os.path.exists(args.baseline):
            old = _load_json(args.baseline, "baseline").get("counts", {})
            for key in (ORPHAN, ISLAND):
                if counts[key] > old.get(key, 0):
                    regressions.append(
                        f"{key} rose from {old.get(key, 0)} to {counts[key]}"
                    )
        if args.as_json:
            json.dump({"date": today.isoformat(), "mode": "survey",
                       "counts": counts, "boot": weight,
                       "results": survey["results"],
                       "regressions": regressions}, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            sys.stdout.write(build_survey_report(
                survey, counts, weight, args.root, today, args.deep_hops))
            if regressions:
                print("\nBASELINE REGRESSION")
                for reg in regressions:
                    print(f"  {reg}")
        return 1 if regressions and args.fail_on_regression else 0

    if not os.path.exists(args.ledger):
        print(f"ERROR: ledger not found at {args.ledger}", file=sys.stderr)
        return 1

    matcher = Matcher(_load_json(args.matcher, "matcher") if args.matcher else None)
    with open(args.ledger, encoding="utf-8") as fh:
        parsed, malformed = parse_ledger(fh.readlines())

    tree = list_tree(args.root)
    results = classify_reachability(parsed, tree, args.root, matcher)
    counts = counts_from(results)
    probes = _load_json(args.probes, "probes") if args.probes else default_probes(tree)
    probe_report = run_lane_probe(results, probes, matcher)
    today = dt.date.today()
    use_report = run_use_readout(results, probe_report, today, matcher)
    forbidden = run_forbidden_check(results, probes, matcher)

    regressions = []
    if args.baseline and os.path.exists(args.baseline):
        regressions = compare_baseline(counts, _load_json(args.baseline, "baseline"))

    if args.write_baseline:
        with open(args.write_baseline, "w", encoding="utf-8") as fh:
            json.dump({"date": today.isoformat(), "counts": counts}, fh, indent=2)
            fh.write("\n")
        print(f"Baseline written to {args.write_baseline}: {counts}")
        return 0

    if args.as_json:
        json.dump({
            "date": today.isoformat(),
            "counts": counts,
            "malformed_lines": len(malformed),
            "unreachable": [
                {"line": r["line_no"], "key": r["key"]}
                for r in results if r["verdict"] == UNREACHABLE
            ],
            "lane": {
                "probes": len(probe_report["runs"]),
                "distinct_injections": probe_report["distinct_injections"],
                "stuck": probe_report["stuck"],
                "unexercised": probe_report["unexercised"],
                "always_injected": probe_report["always_injected"],
            },
            "use": {
                "live": use_report["live"],
                "stamped": use_report["stamped"],
                "never_stamped": use_report["never_stamped"],
                "dead_weight": [r["line_no"] for r in use_report["dead_weight"]],
            },
            "forbidden": {
                "superseded": forbidden["superseded"],
                "hits": forbidden["forbidden_hits"],
                "unexercised": forbidden["unexercised"],
            },
            "regressions": regressions,
        }, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(build_report(
            results, probe_report, use_report, counts, args.ledger, today,
            matcher, regressions, forbidden,
        ))
        if malformed:
            print(f"\nMalformed lines ({len(malformed)}):")
            for line_no, snippet in malformed:
                print(f"  line {line_no}: {snippet}")

    if regressions and args.fail_on_regression:
        return 1
    if forbidden["forbidden_hits"] and args.fail_on_forbidden:
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # Piping into head closes stdout early. Without this the reader gets a
        # traceback for doing something completely reasonable.
        try:
            sys.stdout.close()
        finally:
            os._exit(0)
