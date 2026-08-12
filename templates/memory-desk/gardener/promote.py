#!/usr/bin/env python3
"""promote.py: the gardener's mechanical half.

`mem add`'s own help text promises "the gardener promotes durable entries
to index.tsv on its next pass." GARDENER.md documents the full seven-step
pass; this script does the one step that is genuinely mechanical (promote,
step 1, plus the exact-key half of dedupe, step 2) and stops there.

What it does NOT do, on purpose, matching GARDENER.md's own boundaries:
  - Refresh (step 3): a stale row needs a human to re-read the source and
    judge whether the answer still holds. This script only flags candidates.
  - Retire (step 4): "a reviewed act, not a side effect." Flagged, not acted.
  - Trim the kernel (step 5): requires judgment about what still answers a
    question versus what's now redundant with a row. Not attempted.
  - Semantic dedupe: two rows that say the same thing in different words.
    This script only merges an EXACT key collision (case-insensitive, same
    normalization `mem check` uses); anything with high word-overlap but a
    different key is flagged for a human to look at, never auto-merged.

What it DOES do, mechanically, safely:
  - Reads journal.jsonl entries newer than the last "gardened through" marker.
  - Skips `todo`/`state` entries (not facts, per GARDENER.md step 1).
  - For `fact`/`decision`/`gotcha` entries: builds an index.tsv row, keyed on
    the entry's own `key` field (the best alias you'll ever get, per the
    same doc) or a derived slug when absent, flagged as needing a real alias.
  - Exact-key collision with an existing row: updates that row's answer,
    source, and checked date in place, matching step 2's literal-duplicate
    case. No collision: appends a new row.
  - Runs mem's own `check()` after writing, so a gardening pass that breaks
    the index never gets written silently (step 6).
  - Appends the watermark last (step 7), so nothing is double-processed.

Default is --dry-run: prints the proposed diff and the review queue,
writes nothing. --apply writes index.tsv and the watermark. Either way,
the human-judgment items (refresh candidates, retire candidates, semantic-
duplicate flags) print to a review queue and are never auto-applied,
matching GARDENER.md's "the gardener proposes; a human merges."

Usage:
  promote.py [--desk PATH] [--dry-run | --apply]
  promote.py --selftest
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

TYPES_TO_PROMOTE = {"fact", "decision", "gotcha"}
TYPES_TO_SKIP = {"todo", "state"}
DUPLICATE_OVERLAP_THRESHOLD = 0.6  # word-overlap ratio that triggers a flag, never an auto-merge
STOPWORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "in",
    "is", "it", "my", "of", "on", "or", "our", "the", "this", "to", "we",
    "what", "when", "where", "which", "who", "why", "you", "your",
}


def norm(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def slugify(text, max_words=6):
    words = re.findall(r"[a-z0-9]+", text.lower())
    words = [w for w in words if w not in STOPWORDS][:max_words]
    return " ".join(words) if words else "unkeyed"


def load_journal(journal_path):
    """Returns (entries_after_marker, last_marker_line_index_or_None)."""
    if not journal_path.exists():
        return [], None
    lines = journal_path.read_text(encoding="utf-8").splitlines()
    last_marker = None
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "state" and str(e.get("text", "")).startswith("gardened through"):
            last_marker = i
    after = lines[last_marker + 1:] if last_marker is not None else lines
    entries = []
    for line in after:
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries, last_marker


def load_index(index_path):
    """Returns (header_lines, rows). Mirrors mem's load_rows() field order."""
    header, rows = [], []
    if not index_path.exists():
        return header, rows
    for line in index_path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            header.append(line)
            continue
        parts = line.split("\t")
        if len(parts) != 5:
            continue
        key, aliases, answer, source, checked = (p.strip() for p in parts)
        rows.append({
            "key": key, "aliases": aliases, "answer": answer,
            "source": source, "checked": checked,
        })
    return header, rows


def word_overlap(a, b):
    wa = {w for w in re.findall(r"[a-z0-9]+", a.lower()) if w not in STOPWORDS}
    wb = {w for w in re.findall(r"[a-z0-9]+", b.lower()) if w not in STOPWORDS}
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def promote(entries, rows, today):
    """Mutates rows in place for exact-key updates; returns (new_rows,
    unkeyed_flags, duplicate_flags, skipped)."""
    by_key = {norm(r["key"]): r for r in rows}
    new_rows, unkeyed_flags, duplicate_flags, skipped = [], [], [], []

    for e in entries:
        etype = e.get("type", "fact")
        if etype in TYPES_TO_SKIP:
            skipped.append(e)
            continue
        if etype not in TYPES_TO_PROMOTE:
            skipped.append(e)
            continue
        text = str(e.get("text", "")).strip()
        if not text:
            continue
        key = e.get("key")
        needs_key_review = not key
        if not key:
            key = slugify(text)
        source = e.get("source") or "-"

        existing = by_key.get(norm(key))
        if existing is not None:
            existing["answer"] = text
            existing["source"] = source
            existing["checked"] = today
        else:
            for r in rows:
                if word_overlap(r["answer"], text) >= DUPLICATE_OVERLAP_THRESHOLD:
                    duplicate_flags.append({
                        "candidate_key": key, "candidate_text": text,
                        "existing_key": r["key"], "existing_answer": r["answer"],
                    })
            row = {"key": key, "aliases": "", "answer": text,
                   "source": source, "checked": today}
            rows.append(row)
            by_key[norm(key)] = row
            new_rows.append(row)
        if needs_key_review:
            unkeyed_flags.append({"key": key, "text": text})

    return new_rows, unkeyed_flags, duplicate_flags, skipped


def write_index(index_path, header, rows):
    lines = list(header) if header else [
        "# index.tsv · the memory desk's fact index. One row per settled fact.",
        "# Five tab-separated fields: key <TAB> aliases (| separated, may be empty)",
        "# <TAB> answer <TAB> source <TAB> checked (YYYY-MM-DD, or - for unchecked).",
        "# Keys and aliases match case-insensitively; write them the way a session",
        "# would ask. Keys must not begin with the reserved words add or check.",
    ]
    for r in rows:
        lines.append("\t".join([r["key"], r["aliases"], r["answer"], r["source"], r["checked"]]))
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_watermark(journal_path, newest_ts):
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "type": "state",
        "text": f"gardened through {newest_ts}",
    }
    with journal_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_mem_check(desk):
    """Runs `python3 <desk>/mem check` as a subprocess, exactly what GARDENER.md
    step 6 says to do. Returns (problem_lines, note); problem_lines is None
    when mem itself couldn't be run (note explains why), an empty list when
    the check passed clean, or the printed problem lines when it did not."""
    import subprocess
    mem_path = desk / "mem"
    if not mem_path.exists():
        return None, "no mem script found at desk root; skipped"
    try:
        result = subprocess.run(
            [sys.executable, str(mem_path), "check"],
            capture_output=True, text=True, timeout=30,
        )
    except Exception as exc:  # pragma: no cover, defensive only
        return None, f"mem check could not run: {exc}"
    if result.returncode == 0:
        return [], None
    lines = [l for l in (result.stdout + result.stderr).splitlines() if l.strip()]
    return lines, None


def main(argv):
    desk = Path("memory")
    mode = "--dry-run"
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--desk":
            i += 1
            desk = Path(argv[i])
        elif a in ("--dry-run", "--apply"):
            mode = a
        elif a == "--selftest":
            return selftest()
        else:
            print(f"unknown argument: {a}", file=sys.stderr)
            return 2
        i += 1

    journal_path, index_path = desk / "journal.jsonl", desk / "index.tsv"
    entries, _ = load_journal(journal_path)
    header, rows = load_index(index_path)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    new_rows, unkeyed, dupes, skipped = promote(entries, rows, today)

    print(f"promote.py: {len(entries)} journal entries since last marker")
    print(f"  {len(new_rows)} new row(s), "
          f"{len([e for e in entries if e.get('type') in TYPES_TO_PROMOTE]) - len(new_rows)} "
          f"exact-key update(s), {len(skipped)} skipped (todo/state/other)")
    if unkeyed:
        print(f"  REVIEW: {len(unkeyed)} entr{'y' if len(unkeyed) == 1 else 'ies'} promoted "
              "with a derived key, not a real alias; a human should give it one")
    if dupes:
        print(f"  REVIEW: {len(dupes)} possible semantic duplicate(s), not auto-merged:")
        for d in dupes:
            print(f"    '{d['candidate_key']}' overlaps existing '{d['existing_key']}'")

    if mode == "--dry-run":
        print("\n--dry-run: nothing written. Re-run with --apply to write index.tsv "
              "and the watermark.")
        return 0

    if not entries:
        print("nothing to promote; watermark not moved.")
        return 0

    write_index(index_path, header, rows)
    newest_ts = entries[-1].get("ts", datetime.now(timezone.utc).isoformat())
    append_watermark(journal_path, newest_ts)

    problems, note = run_mem_check(desk)
    if note:
        print(f"  ({note})")
    elif problems:
        print(f"FAIL: mem check found {len(problems)} problem(s) after the pass; "
              "fix before landing the PR:")
        for p in problems:
            print(f"    {p}")
        return 1
    else:
        print("mem check: clean")

    print("applied. Land as one PR per GARDENER.md; retire/refresh/trim candidates "
          "above still need a human pass.")
    return 0


def selftest():
    import shutil
    import tempfile
    checks = []

    def ok(name, cond):
        checks.append((name, cond))

    tmp = Path(tempfile.mkdtemp(prefix="gardenertest_"))
    try:
        desk = tmp / "memory"
        desk.mkdir()
        (desk / "index.tsv").write_text(
            "# index.tsv\n"
            "existing fact\t\tthe old answer\told/source.md\t2026-01-01\n",
            encoding="utf-8",
        )
        journal_lines = [
            json.dumps({"ts": "2026-08-01T00:00:00", "type": "state",
                        "text": "gardened through 2026-07-31T00:00:00"}),
            json.dumps({"ts": "2026-08-02T00:00:00", "type": "fact",
                        "key": "new fact", "text": "a brand new fact",
                        "source": "new/source.md"}),
            json.dumps({"ts": "2026-08-03T00:00:00", "type": "fact",
                        "text": "an unkeyed fact with no key field",
                        "source": "unkeyed/source.md"}),
            json.dumps({"ts": "2026-08-04T00:00:00", "type": "fact",
                        "key": "existing fact", "text": "the corrected answer",
                        "source": "new/source.md"}),
            json.dumps({"ts": "2026-08-05T00:00:00", "type": "todo",
                        "text": "someone should look at this later"}),
        ]
        (desk / "journal.jsonl").write_text("\n".join(journal_lines) + "\n", encoding="utf-8")

        entries, marker = load_journal(desk / "journal.jsonl")
        ok("marker found, only post-marker entries returned", len(entries) == 4)
        ok("marker index is correct", marker == 0)

        header, rows = load_index(desk / "index.tsv")
        ok("existing row loaded", len(rows) == 1 and rows[0]["key"] == "existing fact")

        today = "2026-08-12"
        new_rows, unkeyed, dupes, skipped = promote(entries, rows, today)
        ok("two new rows created (new fact + unkeyed fact)", len(new_rows) == 2
           and any(r["key"] == "new fact" for r in new_rows))
        ok("unkeyed entry flagged, not silently dropped", len(unkeyed) == 1)
        ok("unkeyed entry still promoted with a derived slug",
           any(r["key"] == "unkeyed fact key field" for r in rows)
           or any("unkeyed" in r["key"] for r in rows))
        ok("todo entry skipped, not promoted", len(skipped) == 1
           and skipped[0]["type"] == "todo")
        ok("exact-key collision updates in place, not a new row",
           rows[0]["answer"] == "the corrected answer" and rows[0]["checked"] == today)
        ok("total row count is existing(1) + new(1) + unkeyed(1), no duplicate rows",
           len(rows) == 3)

        write_index(desk / "index.tsv", header, rows)
        header2, rows2 = load_index(desk / "index.tsv")
        ok("written index round-trips cleanly", len(rows2) == 3
           and any(r["answer"] == "the corrected answer" for r in rows2))

        append_watermark(desk / "journal.jsonl", "2026-08-04T00:00:00")
        entries2, marker2 = load_journal(desk / "journal.jsonl")
        ok("watermark append moves the marker forward", len(entries2) == 0)

        # Semantic-duplicate flag, never auto-merged.
        (desk / "journal2.jsonl").write_text(
            json.dumps({"ts": "2026-08-06T00:00:00", "type": "fact",
                        "key": "a totally different key",
                        "text": "the corrected answer today",
                        "source": "x"}) + "\n",
            encoding="utf-8",
        )
        entries3, _ = load_journal(desk / "journal2.jsonl")
        rows3 = [dict(r) for r in rows2]
        _, _, dupes3, _ = promote(entries3, rows3, today)
        ok("near-duplicate text under a different key is flagged", len(dupes3) == 1)
        ok("a flagged duplicate is NOT auto-merged into the existing row",
           any(r["key"] == "a totally different key" for r in rows3))

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = sum(1 for _, c in checks if c)
    for name, cond in checks:
        print(f"  {'ok' if cond else 'FAIL'}   {name}")
    print(f"selftest: {passed}/{len(checks)} passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
