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
        self.tombstones = self.dir / "tombstones.json"
        self.max_working = max_working
        if not self.working.exists():
            self._write(self.working, {"goal": "", "scratchpad": {}, "compactions": 0})
        if not self.facts.exists():
            self._write(self.facts, {})
        if not self.tombstones.exists():
            self._write(self.tombstones, {})
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
        # Re-inserting moves an updated key to the end, so compaction's
        # oldest-first flush is ordered by last update, not first insertion.
        state["scratchpad"].pop(key, None)
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
        """Record a fact as ASSERTED. Nothing an agent stores starts verified.

        Restating an existing key is a supersession, not a silent edit: the
        prior value and its status are logged to the episodic ledger BEFORE
        the overwrite, so a verified fact cannot vanish without a trace and
        the new value starts back at asserted. (Write-tier gap named by the
        Agent Memory Atlas analysis, 2026-08-09: an in-place overwrite inside
        a kit whose rule is that nothing is edited in place.) Restating the
        SAME value is a no-op: status and evidence are untouched, so a
        verified fact is never demoted by repetition.
        """
        stones = self._read(self.tombstones)
        stone = stones.get(f"{category}/{key}", {}).get(str(value))
        if stone is not None:
            raise ValueError(
                f"value rejected for {category}/{key}: {stone['reason']} "
                f"(tombstoned {stone['when']}); a rejected value may not be "
                "silently re-asserted. If the rejection no longer holds, "
                "clear it deliberately with lift_tombstone()."
            )
        facts = self._read(self.facts)
        prior = facts.get(category, {}).get(key)
        if prior is not None and prior.get("value") == value:
            # Restating the same value is a no-op, not a demotion: a verified
            # fact keeps its status and evidence. (Atlas round 2, 2026-08-09:
            # the same-value path silently reset verified to asserted with
            # evidence None, an untraceable demotion the docstring denied.)
            return
        if prior is not None:
            self.log_episode(
                "SUPERSEDED",
                json.dumps({"category": category, "key": key,
                            "prior_value": prior.get("value"),
                            "prior_status": prior.get("status"),
                            "new_value": value}),
                ["supersession"],
            )
        facts.setdefault(category, {})[key] = {
            "value": value, "status": "asserted", "evidence": None,
            "recorded_at": time.time(),
        }
        self._write(self.facts, facts)

    def reject_fact(self, category, key, value, reason):
        """Tombstone a value so it cannot be silently re-asserted.

        A correction that only overwrites is half a correction: the next
        session that re-derives the old value writes it right back, and
        nothing remembers it was ever wrong. The tombstone is a durable
        record keyed on the REJECTED VALUE; store_fact() refuses it until
        lift_tombstone() clears it deliberately. Refuses an empty reason for
        the same cause verify_fact refuses empty evidence.
        """
        if not reason or not str(reason).strip():
            raise ValueError("a tombstone requires a reason; an unexplained "
                             "rejection is as unauditable as an unexplained "
                             "verification")
        stones = self._read(self.tombstones)
        stones.setdefault(f"{category}/{key}", {})[str(value)] = {
            "reason": str(reason),
            "when": time.strftime("%Y-%m-%d"),
        }
        self._write(self.tombstones, stones)
        facts = self._read(self.facts)
        entry = facts.get(category, {}).get(key)
        if entry is not None and entry.get("value") == value:
            del facts[category][key]
            self._write(self.facts, facts)
        self.log_episode(
            "REJECTED",
            json.dumps({"category": category, "key": key, "value": value,
                        "reason": str(reason)}),
            ["tombstone"],
        )

    def lift_tombstone(self, category, key, value, reason):
        """Clear a tombstone, on the record. The lift logs an episode with
        its own reason; the tombstone row is removed, the episodic trail of
        both the rejection and the lift survives."""
        if not reason or not str(reason).strip():
            raise ValueError("lifting a tombstone requires a reason")
        stones = self._read(self.tombstones)
        row = stones.get(f"{category}/{key}", {})
        if str(value) not in row:
            raise KeyError(f"no tombstone at {category}/{key} for {value!r}")
        del row[str(value)]
        if not row:
            del stones[f"{category}/{key}"]
        self._write(self.tombstones, stones)
        self.log_episode(
            "TOMBSTONE_LIFTED",
            json.dumps({"category": category, "key": key, "value": value,
                        "reason": str(reason)}),
            ["tombstone"],
        )

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

    def build_context(self, query="", max_episodes=MAX_EPISODES_IN_CONTEXT,
                      as_of=None):
        """One deterministic context block: goal, scratchpad, facts, episodes.

        Episode selection is newest-first, with exact keyword overlap against
        the query promoting matches ahead of mere recency. Deterministic and
        greppable; it will not catch a paraphrase, and says so in the header.

        as_of (unix timestamp) replays the learned-at axis: facts recorded
        after that moment are excluded and episodes are cut at it, so you can
        ask "what did the memory know when that session ran", which is the
        question a stale-belief postmortem actually needs. Facts written
        before recorded_at existed carry no stamp and are always included,
        stated in the block header so the limit is visible, not silent. This
        filters learned-at only; a valid-at axis (when the fact was true in
        the world) is a schema decision for your ledger, not this engine.
        """
        state = self._read(self.working)
        facts = self._read(self.facts)
        qwords = {w for w in query.lower().split() if len(w) > 2}

        rows = []
        for line in self.episodes.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        if as_of is not None:
            rows = [r for r in rows if r.get("ts", 0) <= as_of]
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

        header = "=== MEMORY (retrieval: recency + exact keyword; no paraphrase match)"
        if as_of is not None:
            header += (" | as-of replay: facts/episodes learned after the "
                       "cutoff excluded; unstamped facts always included")
        out = [header + " ==="]
        if state.get("goal"):
            out.append(f"goal: {state['goal']}")
        for k, v in state.get("scratchpad", {}).items():
            out.append(f"working.{k}: {v}")
        for cat, entries in facts.items():
            for k, e in entries.items():
                if as_of is not None and e.get("recorded_at") is not None \
                        and e["recorded_at"] > as_of:
                    continue
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

        # Overwrite discipline: restating a verified fact logs the prior
        # value as a SUPERSEDED episode first, and the new value starts back
        # at asserted. A verified status may never vanish without a trace.
        mem.store_fact("env", "python", ">=3.11")
        f = mem._read(mem.facts)["env"]["python"]
        ok("an overwritten fact resets to asserted", f["status"] == "asserted")
        eps = [json.loads(l) for l in mem.episodes.read_text().splitlines() if l.strip()]
        sup = [e for e in eps if e["action"] == "SUPERSEDED"]
        ok("the prior value and status are logged before the overwrite",
           len(sup) == 1 and ">=3.8" in sup[0]["outcome"]
           and "verified" in sup[0]["outcome"])
        mem.store_fact("env", "python", ">=3.11")
        eps2 = [json.loads(l) for l in mem.episodes.read_text().splitlines() if l.strip()]
        ok("restating the same value is not a supersession",
           len([e for e in eps2 if e["action"] == "SUPERSEDED"]) == 1)
        mem.verify_fact("env", "python", "CI run 42")
        mem.store_fact("env", "python", ">=3.11")
        kept = mem._read(mem.facts)["env"]["python"]
        ok("restating the same value keeps verified status and evidence",
           kept["status"] == "verified" and kept["evidence"] == "CI run 42")

        # tombstones: a rejected value cannot be silently re-asserted
        mem.store_fact("env", "db", "postgres 14")
        mem.reject_fact("env", "db", "postgres 14",
                        "prod runs 15; 14 was a stale doc claim")
        gone = mem._read(mem.facts).get("env", {}).get("db")
        ok("rejecting the current value removes the fact entry", gone is None)
        blocked = False
        try:
            mem.store_fact("env", "db", "postgres 14")
        except ValueError:
            blocked = True
        ok("a tombstoned value is refused on re-assertion", blocked)
        mem.store_fact("env", "db", "postgres 15")
        ok("a different value for the same key still stores",
           mem._read(mem.facts)["env"]["db"]["value"] == "postgres 15")
        empty_reason = False
        try:
            mem.reject_fact("env", "db", "postgres 15", "  ")
        except ValueError:
            empty_reason = True
        ok("a tombstone refuses an empty reason", empty_reason)
        mem.lift_tombstone("env", "db", "postgres 14",
                           "rejection superseded in test")
        mem.store_fact("env", "db2", "x")
        mem.reject_fact("env", "db2", "x", "r")
        eps3 = [json.loads(l) for l in
                mem.episodes.read_text().splitlines() if l.strip()]
        ok("rejection and lift both leave episodic records",
           any(e["action"] == "REJECTED" for e in eps3)
           and any(e["action"] == "TOMBSTONE_LIFTED" for e in eps3))

        # bi-temporal replay: as_of excludes later-learned facts
        cutoff = time.time()
        time.sleep(0.01)
        mem.store_fact("env", "later", "learned after cutoff")
        ctx_now = mem.build_context()
        ctx_then = mem.build_context(as_of=cutoff)
        ok("as_of replay excludes facts learned after the cutoff",
           "later" in ctx_now and "later" not in ctx_then)
        ok("as_of replay states its unstamped-facts limit in the header",
           "unstamped facts always included" in ctx_then.splitlines()[0])
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
