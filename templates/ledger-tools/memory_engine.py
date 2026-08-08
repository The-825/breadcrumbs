#!/usr/bin/env python3
"""File-native tiered memory for an agent loop: working, episodic, semantic.

ASSUMES an agent execution loop you control (you build the prompt, you call the
model, you log what happened). Stdlib only, no server, no vector store. If your
harness already injects a rules file and a session-state doc, this is the
runnable composition of that same pattern, not a replacement for it.

WHY THREE TIERS, not one file. Different facts decay on different clocks, and
one undifferentiated store forces one clock on all of them:

  working   session_state.json   The active goal and scratchpad. Rewritten
                                 continuously, worthless next week.
  episodic  episodes.jsonl       What happened, append-only. Merge-safe under
                                 parallel writers because every line is
                                 independent (pair with merge=union).
  semantic  facts.json           Settled invariants. Small, deduplicated, the
                                 only tier worth injecting into every prompt.

THE TWO RULES THIS ENCODES, which are the point:

1. A fact is ASSERTED until something other than its author says otherwise.
   store_fact() records status "asserted". Promoting to "verified" requires
   naming the oracle (a CI run, a data assertion, a human ruling) via
   verify_fact(). The engine refuses a verified status with no evidence,
   because an agent marking its own claim verified is the failure this whole
   kit exists to prevent.

2. Compaction flushes DOWN, never deletes. When the scratchpad hits its cap,
   the overflow is appended to the episodic ledger before the working file
   shrinks. The record of what happened survives; only the residency changes.

HONEST LIMITS, so you do not trust it past what it does:

- Retrieval is recency plus exact keyword overlap. It is deterministic and
  inspectable with cat and grep, and it will miss a paraphrase. If you need
  semantic recall, add it as a separate layer; do not pretend this one has it.
- Atomic per-file writes (temp file + rename) protect against a crash mid-
  write. They do NOT make concurrent read-modify-write safe: two agents
  updating session_state.json can still lose an update. Working state is
  per-agent by design; give parallel agents separate memory dirs and share
  only the episodic ledger, which is append-only and safe.
- No decay, no use-stamps, no reachability scoring. Those are the measurement
  layer (docs/memory-measurement.md, conclusions_audit.py, retrieval_exam.py)
  and they run OVER stores like this one rather than inside it.

Usage:
    python3 memory_engine.py --selftest
    python3 memory_engine.py --demo   (writes to a temp dir, prints a context block)

As a library:
    from memory_engine import MemoryEngine
    mem = MemoryEngine(".memory")
    mem.set_goal("migrate the sync job to async")
    mem.note("step_1", "connection pool blueprint written")
    mem.log_episode("TEST", "pool latency down 40 percent", ["perf"])
    mem.store_fact("environment", "python", ">=3.11")
    mem.verify_fact("environment", "python", evidence="ci run 4412 green on 3.11")
    print(mem.build_context("async pool tests"))
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

# Scratchpad entries kept resident before the overflow flushes to the episodic
# ledger. Small on purpose: the working tier is what every prompt pays for.
MAX_WORKING_ENTRIES = 8
# Episodes injected into a context block. The ledger itself is unbounded; this
# caps what a prompt pays, not what is remembered.
MAX_EPISODES_IN_CONTEXT = 5


class MemoryEngine:
    def __init__(self, memory_dir=".memory", max_working=MAX_WORKING_ENTRIES):
        self.dir = Path(memory_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.working = self.dir / "session_state.json"
        self.episodes = self.dir / "episodes.jsonl"
        self.facts = self.dir / "facts.json"
        self.max_working = max_working
        if not self.working.exists():
            self._write(self.working, {"goal": "", "scratchpad": {}, "compactions": 0})
        if not self.facts.exists():
            self._write(self.facts, {})
        self.episodes.touch(exist_ok=True)

    # -- storage primitives ---------------------------------------------------

    @staticmethod
    def _read(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    @staticmethod
    def _write(path, data):
        # Atomic against a crash mid-write: never leaves a half-written JSON
        # file. NOT a concurrency lock; see the module header.
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            os.replace(tmp, path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    # -- working tier ---------------------------------------------------------

    def set_goal(self, goal):
        state = self._read(self.working)
        state["goal"] = goal
        self._write(self.working, state)

    def note(self, key, value):
        """Record working state. Triggers compaction at the cap."""
        state = self._read(self.working)
        state["scratchpad"][key] = value
        self._write(self.working, state)
        if len(state["scratchpad"]) >= self.max_working:
            self.compact()

    def compact(self):
        """Flush the oldest scratchpad entries down to the episodic ledger.

        Flush-then-shrink, in that order: if the process dies between the two
        writes, the worst case is a duplicate episode, never a lost one.
        """
        state = self._read(self.working)
        pad = state.get("scratchpad", {})
        if len(pad) <= 2:
            return
        keys = list(pad.keys())
        overflow, keep = keys[:-2], keys[-2:]
        self.log_episode(
            "COMPACTION",
            json.dumps({k: pad[k] for k in overflow}),
            ["compaction"],
        )
        state["scratchpad"] = {k: pad[k] for k in keep}
        state["compactions"] = state.get("compactions", 0) + 1
        self._write(self.working, state)

    # -- episodic tier --------------------------------------------------------

    def log_episode(self, action, outcome, tags=None):
        row = {"ts": time.time(), "action": action, "outcome": outcome,
               "tags": tags or []}
        with open(self.episodes, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")

    # -- semantic tier --------------------------------------------------------

    def store_fact(self, category, key, value):
        """Record a fact as ASSERTED. Nothing an agent stores starts verified."""
        facts = self._read(self.facts)
        facts.setdefault(category, {})[key] = {
            "value": value, "status": "asserted", "evidence": None,
        }
        self._write(self.facts, facts)

    def verify_fact(self, category, key, evidence):
        """Promote to verified, naming the oracle. Refuses empty evidence."""
        if not evidence or not str(evidence).strip():
            raise ValueError(
                "verified requires naming the oracle (a CI run, a data "
                "assertion, a human ruling); an agent may not mark its own "
                "claim verified with nothing behind it"
            )
        facts = self._read(self.facts)
        entry = facts.get(category, {}).get(key)
        if entry is None:
            raise KeyError(f"no fact at {category}/{key} to verify")
        entry["status"] = "verified"
        entry["evidence"] = str(evidence)
        self._write(self.facts, facts)

    # -- retrieval ------------------------------------------------------------

    def build_context(self, query="", max_episodes=MAX_EPISODES_IN_CONTEXT):
        """One deterministic context block: goal, scratchpad, facts, episodes.

        Episode selection is newest-first, with exact keyword overlap against
        the query promoting matches ahead of mere recency. Deterministic and
        greppable; it will not catch a paraphrase, and says so in the header.
        """
        state = self._read(self.working)
        facts = self._read(self.facts)
        qwords = {w for w in query.lower().split() if len(w) > 2}

        rows = []
        for line in self.episodes.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        rows.reverse()  # newest first
        matched = [r for r in rows if qwords and (
            qwords & set((r["action"] + " " + r["outcome"]).lower().split()))]
        picked, seen = [], set()
        for r in matched + rows:
            rid = id(r)
            if rid not in seen:
                picked.append(r)
                seen.add(rid)
            if len(picked) >= max_episodes:
                break

        out = ["=== MEMORY (retrieval: recency + exact keyword; no paraphrase match) ==="]
        if state.get("goal"):
            out.append(f"goal: {state['goal']}")
        for k, v in state.get("scratchpad", {}).items():
            out.append(f"working.{k}: {v}")
        for cat, entries in facts.items():
            for k, e in entries.items():
                tag = e["status"]
                if tag == "verified":
                    tag += f" ({e['evidence']})"
                out.append(f"fact.{cat}.{k}: {e['value']} [{tag}]")
        for r in picked:
            out.append(f"episode: [{r['action']}] {r['outcome']}")
        out.append("=== END MEMORY ===")
        return "\n".join(out)


# -- selftest -----------------------------------------------------------------

def selftest():
    import shutil
    checks = []

    def ok(name, cond):
        checks.append((name, cond))

    tmp = tempfile.mkdtemp(prefix="memtest_")
    try:
        mem = MemoryEngine(tmp, max_working=4)
        mem.set_goal("test the tiers")
        ok("goal persists", mem._read(mem.working)["goal"] == "test the tiers")

        mem.store_fact("env", "python", ">=3.8")
        f = mem._read(mem.facts)["env"]["python"]
        ok("stored fact starts asserted, never verified", f["status"] == "asserted")

        try:
            mem.verify_fact("env", "python", evidence="")
            ok("empty evidence refused", False)
        except ValueError:
            ok("empty evidence refused", True)

        mem.verify_fact("env", "python", evidence="ci run green on 3.8")
        f = mem._read(mem.facts)["env"]["python"]
        ok("verification names its oracle", f["evidence"] == "ci run green on 3.8")

        try:
            mem.verify_fact("env", "missing", evidence="x")
            ok("verifying a missing fact raises", False)
        except KeyError:
            ok("verifying a missing fact raises", True)

        for i in range(4):
            mem.note(f"s{i}", f"step {i}")  # 4th note hits the cap
        state = mem._read(mem.working)
        ok("compaction shrank the scratchpad", len(state["scratchpad"]) == 2)
        ok("compaction counted", state["compactions"] == 1)
        eps = [json.loads(l) for l in mem.episodes.read_text().splitlines() if l.strip()]
        ok("overflow flushed DOWN, not deleted",
           any(e["action"] == "COMPACTION" and "s0" in e["outcome"] for e in eps))

        mem.log_episode("BENCH", "pool latency down", ["perf"])
        ctx = mem.build_context("latency pool")
        ok("query-matched episode surfaces", "pool latency down" in ctx)
        ok("context names its retrieval limit", "no paraphrase match" in ctx)
        ok("verified fact carries evidence inline", "ci run green on 3.8" in ctx)

        ctx2 = mem.build_context("latency pool")
        ok("retrieval is deterministic", ctx == ctx2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [n for n, c in checks if not c]
    for name, cond in checks:
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    print(f"selftest: {len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


def demo():
    with tempfile.TemporaryDirectory() as tmp:
        mem = MemoryEngine(tmp)
        mem.set_goal("demo the three tiers")
        mem.store_fact("stack", "runtime", "python >=3.8")
        mem.note("step_1", "engine initialized")
        mem.log_episode("DEMO", "context block built from all three tiers", ["demo"])
        print(mem.build_context("demo context"))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    sys.exit(selftest() if a.selftest else demo() if a.demo else 0)
