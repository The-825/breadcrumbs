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

1. A fact is ASSERTED until an independent authority says otherwise.
   store_fact() records both the asserting actor and its authority class.
   Promoting to "verified" requires evidence plus a distinct tool or human
   verifier. Agent authority can never verify, and repetition cannot promote,
   because an agent laundering its own claim through added provenance is the
   failure this whole kit exists to prevent.

2. Compaction flushes DOWN, never deletes. When the scratchpad hits its cap,
   the overflow is appended to the episodic ledger before the working file
   shrinks. The record of what happened survives; only the residency changes.

HONEST LIMITS, so you do not trust it past what it does:

- Retrieval fuses lexical, action/tag, and recency ranks. It is deterministic
  and inspectable with cat and grep, and it will miss a paraphrase. If you need
  semantic recall, add it as a separate layer; do not pretend this one has it.
- Atomic per-file writes (temp file + rename) protect against a crash mid-
  write. They do NOT make concurrent read-modify-write safe: two agents
  updating session_state.json can still lose an update. Working state is
  per-agent by design; give parallel agents separate memory dirs and share
  only the episodic ledger, which is append-only and safe.
- No decay, no use-stamps, no reachability scoring. Those are the measurement
  layer (docs/memory-measurement.md, conclusions_audit.py, retrieval_exam.py)
  and they run OVER stores like this one rather than inside it.

DESIGN REFERENCES. The episode-to-fact provenance shape follows Graphiti's
public episode lineage model, and the multi-signal read path follows the same
semantic-plus-lexical fusion direction described by Mem0. The contradiction
proposal shape follows Nacre's separation between resolution and mutation,
with one stricter rule: evaluator failure stays UNKNOWN instead of becoming a
negative result. This implementation is independent, stdlib-only, and uses no
code from any of those projects:

  https://github.com/getzep/graphiti
  https://github.com/mem0ai/mem0
  https://github.com/bofeizhu/nacre

Usage:
    python3 memory_engine.py --selftest
    python3 memory_engine.py --demo   (writes to a temp dir, prints a context block)

As a library:
    from memory_engine import MemoryEngine
    mem = MemoryEngine(".memory")
    mem.set_goal("migrate the sync job to async")
    mem.note("step_1", "connection pool blueprint written")
    mem.log_episode("TEST", "pool latency down 40 percent", ["perf"])
    mem.store_fact("environment", "python", ">=3.11",
                   asserted_by="agent:runtime-reader")
    mem.verify_fact("environment", "python",
                    evidence="ci run 4412 green on 3.11",
                    verified_by="tool:ci", verification_authority="tool")
    print(mem.build_context("async pool tests"))
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
import uuid
from pathlib import Path

# Scratchpad entries kept resident before the overflow flushes to the episodic
# ledger. Small on purpose: the working tier is what every prompt pays for.
MAX_WORKING_ENTRIES = 8
# Episodes injected into a context block. The ledger itself is unbounded; this
# caps what a prompt pays, not what is remembered.
MAX_EPISODES_IN_CONTEXT = 5
AUTHORITY_CLASSES = frozenset(("agent", "tool", "human"))


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
        """Append an event and return its stable provenance handle."""
        row = {"episode_id": str(uuid.uuid4()), "ts": time.time(),
               "action": action, "outcome": outcome, "tags": tags or []}
        with open(self.episodes, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
        return row["episode_id"]

    # -- semantic tier --------------------------------------------------------

    @staticmethod
    def _normalized_value(value):
        """Normalize only enough for the exact-match fast path."""
        return " ".join(str(value).casefold().split())

    @staticmethod
    def _validity_windows_do_not_overlap(left, right):
        """Return True only when two fully bounded windows are disjoint."""
        left_from, left_until = left.get("valid_from"), left.get("valid_until")
        right_from = right.get("valid_from")
        right_until = right.get("valid_until")
        if None in (left_from, left_until, right_from, right_until):
            return False
        return left_until < right_from or right_until < left_from

    def propose_contradiction(self, category, key, candidate_value,
                              valid_from=None, valid_until=None,
                              evaluator=None):
        """Return a typed contradiction proposal without changing storage.

        Exact normalized values become corroboration proposals. Different
        values with fully bounded, disjoint validity windows may coexist.
        Every other comparison needs an external evaluator that returns a
        mapping with verdict "contradiction", "compatible", or "unknown"
        and a non-empty reason. Missing, malformed, or failed evaluation is
        UNKNOWN. This method never calls a mutation path.
        """
        facts = self._read(self.facts)
        existing = facts.get(category, {}).get(key)
        candidate = {"value": candidate_value, "valid_from": valid_from,
                     "valid_until": valid_until}
        base = {"category": category, "key": key, "existing": existing,
                "candidate": candidate, "mutates": False}
        if existing is None:
            return {**base, "outcome": "new_fact", "verdict": "compatible",
                    "reason": "no existing fact uses this category and key"}
        if self._normalized_value(existing.get("value")) == \
                self._normalized_value(candidate_value):
            return {**base, "outcome": "corroborate",
                    "verdict": "compatible",
                    "reason": "normalized values match exactly"}
        if self._validity_windows_do_not_overlap(existing, candidate):
            return {**base, "outcome": "coexist",
                    "verdict": "compatible",
                    "reason": "fully bounded validity windows do not overlap"}
        if evaluator is None:
            return {**base, "outcome": "review", "verdict": "unknown",
                    "reason": "different values overlap or lack complete "
                              "validity bounds; no evaluator was supplied"}
        try:
            result = evaluator(existing.copy(), candidate.copy())
        except Exception as exc:
            return {**base, "outcome": "review", "verdict": "unknown",
                    "reason": "contradiction evaluator failed: "
                              f"{type(exc).__name__}"}
        if not isinstance(result, dict):
            return {**base, "outcome": "review", "verdict": "unknown",
                    "reason": "contradiction evaluator returned a malformed result"}
        verdict = result.get("verdict")
        reason = str(result.get("reason", "")).strip()
        if verdict not in ("contradiction", "compatible", "unknown") or not reason:
            return {**base, "outcome": "review", "verdict": "unknown",
                    "reason": "contradiction evaluator returned a malformed result"}
        outcome = {"contradiction": "review_replacement",
                   "compatible": "coexist", "unknown": "review"}[verdict]
        return {**base, "outcome": outcome, "verdict": verdict,
                "reason": reason}

    def store_fact(self, category, key, value, valid_from=None,
                   valid_until=None, scope="internal", source_episode_ids=None,
                   asserted_by="agent:unspecified", assertion_authority="agent"):
        """Record a fact as ASSERTED. Nothing an agent stores starts verified.

        valid_from / valid_until (optional, unix timestamps) are the VALID-AT
        axis: when the fact was true in the world, distinct from recorded_at
        (when the memory learned it). scope is the AUDIENCE axis: "public",
        "internal" (default; fail closed), or "regulated". Retrieval filters
        on both; see build_context. source_episode_ids optionally links the
        derived fact to the exact append-only events that produced it. Unknown
        episode ids are refused rather than stored as decorative provenance.

        Restating an existing key is a supersession, not a silent edit: the
        prior value and its status are logged to the episodic ledger BEFORE
        the overwrite, so a verified fact cannot vanish without a trace and
        the new value starts back at asserted. (Write-tier gap named by the
        Agent Memory Atlas analysis, 2026-08-09: an in-place overwrite inside
        a kit whose rule is that nothing is edited in place.) Restating the
        SAME value is a no-op: status and evidence are untouched, so a
        verified fact is never demoted by repetition.
        """
        asserted_by = str(asserted_by).strip()
        if not asserted_by:
            raise ValueError("asserted_by must name the actor that made the claim")
        if assertion_authority not in AUTHORITY_CLASSES:
            raise ValueError(
                f"unknown assertion authority {assertion_authority!r}: use "
                "agent, tool, or human"
            )
        sources = list(dict.fromkeys(source_episode_ids or []))
        if sources:
            known = {
                row.get("episode_id")
                for row in self._load_episodes()
                if row.get("episode_id")
            }
            missing = [source for source in sources if source not in known]
            if missing:
                raise ValueError(
                    "unknown source episode id(s): " + ", ".join(missing)
                )
        stones = self._read(self.tombstones)
        stone = stones.get(f"{category}/{key}", {}).get(str(value))
        if stone is not None:
            redirect = (f" Use instead: {stone['alternative']}."
                        if stone.get("alternative") else "")
            raise ValueError(
                f"value rejected for {category}/{key}: {stone['reason']} "
                f"(tombstoned {stone['when']}); a rejected value may not be "
                "silently re-asserted. If the rejection no longer holds, "
                f"clear it deliberately with lift_tombstone().{redirect}"
            )
        facts = self._read(self.facts)
        prior = facts.get(category, {}).get(key)
        if prior is not None and prior.get("value") == value:
            # Restating the same value is a no-op, not a demotion: a verified
            # fact keeps its status and evidence. New source links still
            # accumulate, because a second independent observation is useful
            # provenance even when it does not change the answer.
            existing_sources = prior.get("source_episode_ids", [])
            merged_sources = list(dict.fromkeys(existing_sources + sources))
            if merged_sources != existing_sources:
                self.log_episode(
                    "PROVENANCE_LINKED",
                    json.dumps({"category": category, "key": key,
                                "value": value,
                                "source_episode_ids": sources}),
                    ["provenance"],
                )
                prior["source_episode_ids"] = merged_sources
                self._write(self.facts, facts)
            return
        if prior is not None:
            self.log_episode(
                "SUPERSEDED",
                json.dumps({"category": category, "key": key,
                            "prior_value": prior.get("value"),
                            "prior_status": prior.get("status"),
                            "prior_source_episode_ids":
                                prior.get("source_episode_ids", []),
                            "new_value": value,
                            "new_source_episode_ids": sources}),
                ["supersession"],
            )
        if scope not in ("public", "internal", "regulated"):
            raise ValueError(f"unknown scope {scope!r}: use public, internal, "
                             "or regulated")
        entry = {
            "value": value, "status": "asserted", "evidence": None,
            "recorded_at": time.time(), "scope": scope,
            "asserted_by": asserted_by,
            "assertion_authority": assertion_authority,
        }
        if sources:
            entry["source_episode_ids"] = sources
        if valid_from is not None:
            entry["valid_from"] = valid_from
        if valid_until is not None:
            entry["valid_until"] = valid_until
        facts.setdefault(category, {})[key] = entry
        self._write(self.facts, facts)

    def reject_fact(self, category, key, value, reason, alternative=None):
        """Tombstone a value so it cannot be silently re-asserted.

        A correction that only overwrites is half a correction: the next
        session that re-derives the old value writes it right back, and
        nothing remembers it was ever wrong. The tombstone is a durable
        record keyed on the REJECTED VALUE; store_fact() refuses it until
        lift_tombstone() clears it deliberately. Refuses an empty reason for
        the same cause verify_fact refuses empty evidence.

        `alternative` is optional and answers the question the refusal
        raises: not just "this value is wrong" but "use this instead". A
        rejection that names the better value turns the next session's dead
        end into a redirect; without it, the session that hits the tombstone
        still has to re-derive what the right value is.
        """
        if not reason or not str(reason).strip():
            raise ValueError("a tombstone requires a reason; an unexplained "
                             "rejection is as unauditable as an unexplained "
                             "verification")
        stones = self._read(self.tombstones)
        stone = {
            "reason": str(reason),
            "when": time.strftime("%Y-%m-%d"),
        }
        if alternative is not None and str(alternative).strip():
            stone["alternative"] = str(alternative)
        stones.setdefault(f"{category}/{key}", {})[str(value)] = stone
        self._write(self.tombstones, stones)
        facts = self._read(self.facts)
        entry = facts.get(category, {}).get(key)
        if entry is not None and entry.get("value") == value:
            del facts[category][key]
            self._write(self.facts, facts)
        record = {"category": category, "key": key, "value": value,
                  "reason": str(reason)}
        if "alternative" in stone:
            record["alternative"] = stone["alternative"]
        self.log_episode("REJECTED", json.dumps(record), ["tombstone"])

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

    def verify_fact(self, category, key, evidence, verified_by=None,
                    verification_authority=None):
        """Promote through a distinct tool or human verifier.

        Stamps verified_at (unix timestamp), distinct from recorded_at. This
        is the trust-axis fix (Agent Memory Atlas, 2026-08-10 review): an
        as-of replay used to ask only "did the memory KNOW this fact yet",
        never "had it been VERIFIED yet", so a fact verified weeks after it
        was recorded replayed as verified at any as-of between the two, an
        oracle that did not exist at the replayed moment. build_context now
        checks both timestamps.
        """
        if not evidence or not str(evidence).strip():
            raise ValueError(
                "verified requires naming the oracle (a CI run, a data "
                "assertion, a human ruling); an agent may not mark its own "
                "claim verified with nothing behind it"
            )
        verifier = str(verified_by or "").strip()
        if not verifier:
            raise ValueError("verified_by must name the independent verifier")
        if verification_authority not in AUTHORITY_CLASSES:
            raise ValueError(
                f"unknown verification authority {verification_authority!r}: "
                "use agent, tool, or human"
            )
        if verification_authority == "agent":
            raise ValueError(
                "agent authority may assert but may not promote a claim to verified"
            )
        facts = self._read(self.facts)
        entry = facts.get(category, {}).get(key)
        if entry is None:
            raise KeyError(f"no fact at {category}/{key} to verify")
        if verifier == entry.get("asserted_by"):
            raise ValueError("the asserting actor may not verify its own claim")
        entry["status"] = "verified"
        entry["evidence"] = str(evidence)
        entry["verified_by"] = verifier
        entry["verification_authority"] = verification_authority
        entry["verified_at"] = time.time()
        entry.pop("verified_at_inferred", None)
        self._write(self.facts, facts)

    def backfill_verified_at(self):
        """One-time migration: give existing verified facts a verified_at.

        Ledgers written before this fix have verified facts with no
        verified_at at all, the strict read (missing = unknown = always
        downgrades under as_of) would make old data look LESS trustworthy
        under replay than it did before this fix shipped, which is not an
        improvement, it is a new, unearned regression. The soft backfill
        instead sets verified_at = recorded_at (the best signal available:
        we don't know exactly when verification happened, only that the
        fact existed by then) and tags the entry verified_at_inferred: true
        so the distinction between an OBSERVED and an INFERRED timestamp
        survives for any code or audit that later needs to tell them apart.
        Idempotent: does nothing to an entry that already carries a real
        verified_at. Returns the count of entries backfilled.
        """
        facts = self._read(self.facts)
        n = 0
        for entries in facts.values():
            for entry in entries.values():
                if entry.get("status") == "verified" \
                        and entry.get("verified_at") is None:
                    entry["verified_at"] = entry.get("recorded_at", 0)
                    entry["verified_at_inferred"] = True
                    n += 1
        if n:
            self._write(self.facts, facts)
        return n

    # -- retrieval ------------------------------------------------------------

    SCOPE_ORDER = {"public": 0, "internal": 1, "regulated": 2}

    @staticmethod
    def _tokens(text):
        return set(re.findall(r"[a-z0-9_]+", str(text).lower()))

    def _load_episodes(self):
        rows = []
        for line in self.episodes.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    def _rank_episodes(self, rows, query):
        """Fuse lexical, action/tag, and recency ranks deterministically.

        Reciprocal rank fusion combines ordinal ranks instead of incomparable
        raw scores. A query-less read remains newest-first. Stable list indexes
        break exact ties, so identical inputs always produce identical output.
        """
        if not rows:
            return []
        newest = list(reversed(rows))
        qtokens = self._tokens(query)
        if not qtokens:
            return newest

        lexical = sorted(
            newest,
            key=lambda row: len(
                qtokens & self._tokens(row.get("outcome", ""))
            ),
            reverse=True,
        )
        action_tag = sorted(
            newest,
            key=lambda row: len(
                qtokens & self._tokens(
                    row.get("action", "") + " "
                    + " ".join(row.get("tags", []))
                )
            ),
            reverse=True,
        )
        signals = ((lexical, 3.0), (action_tag, 2.0), (newest, 1.0))
        scores = {id(row): 0.0 for row in rows}
        for ranked, weight in signals:
            for rank, row in enumerate(ranked, start=1):
                scores[id(row)] += weight / (60 + rank)
        positions = {id(row): index for index, row in enumerate(newest)}
        return sorted(
            newest,
            key=lambda row: (-scores[id(row)], positions[id(row)]),
        )

    def build_context(self, query="", max_episodes=MAX_EPISODES_IN_CONTEXT,
                      as_of=None, valid_at=None, audience=None):
        """One deterministic context block: goal, scratchpad, facts, episodes.

        Episode selection uses deterministic reciprocal rank fusion over three
        inspectable signals: lexical overlap in the outcome, action/tag overlap,
        and recency. It will not catch a paraphrase, and says so in the header.

        as_of (unix timestamp) replays the learned-at axis: facts recorded
        after that moment are excluded and episodes are cut at it, so you can
        ask "what did the memory know when that session ran", which is the
        question a stale-belief postmortem actually needs. Facts written
        before recorded_at existed carry no stamp and are always included,
        stated in the block header so the limit is visible, not silent. This
        filters learned-at. It ALSO replays the trust axis: a fact verified
        after as_of shows as asserted, not verified, in the replayed view
        (storage is untouched), because "the memory knew the value" and "the
        value had been verified" are different claims and a replay that
        conflates them lends a past belief an oracle it did not have yet.

        valid_at (unix timestamp) filters the VALID-AT axis: facts whose
        valid_from/valid_until window excludes that moment are dropped; facts
        carrying no window are always included (stated in the header). The
        two clocks compose: as_of + valid_at asks "what did we believe at T
        about what was true at T2", the stale-belief postmortem query.

        audience filters the SCOPE axis at the point of assembly, not at the
        point of writing: audience="public" surfaces only public-scoped
        facts; "internal" surfaces public + internal; None (default) applies
        no scope filter. Pre-scope facts with no scope field count as
        internal (fail closed against a public audience). This makes the
        publication boundary mechanical: a public-bound context cannot carry
        a regulated fact no matter what the composing session forgets.
        """
        state = self._read(self.working)
        facts = self._read(self.facts)

        rows = []
        # The episodic tier carries no scope field, and supersession episodes
        # embed prior VALUES, so under any audience filter episodes are
        # omitted entirely: fail closed rather than leak through the side door
        # (found by this module's own selftest, 2026-08-10).
        if audience is None:
            rows = self._load_episodes()
        if as_of is not None:
            rows = [r for r in rows if r.get("ts", 0) <= as_of]
        picked = self._rank_episodes(rows, query)[:max_episodes]

        header = ("=== MEMORY (retrieval: reciprocal-rank fusion over lexical, "
                  "action/tag, and recency signals; no paraphrase match)")
        if as_of is not None:
            header += (" | as-of replay: facts/episodes learned after the "
                       "cutoff excluded; unstamped facts always included")
        if valid_at is not None:
            header += (" | valid-at filter: facts windowed away from the "
                       "moment excluded; unwindowed facts always included")
        if audience is not None:
            header += (f" | audience: {audience} (higher scopes excluded; "
                       "episodes omitted: the episodic tier is unscoped)")

        out = [header + " ==="]
        if state.get("goal"):
            out.append(f"goal: {state['goal']}")
        for k, v in state.get("scratchpad", {}).items():
            out.append(f"working.{k}: {v}")
        clearance = self.SCOPE_ORDER.get(audience) if audience else None
        for cat, entries in facts.items():
            for k, e in entries.items():
                if as_of is not None and e.get("recorded_at") is not None \
                        and e["recorded_at"] > as_of:
                    continue
                if valid_at is not None:
                    vf, vu = e.get("valid_from"), e.get("valid_until")
                    if (vf is not None and valid_at < vf) or \
                            (vu is not None and valid_at > vu):
                        continue
                if clearance is not None:
                    level = self.SCOPE_ORDER.get(e.get("scope", "internal"), 1)
                    if level > clearance:
                        continue
                tag = e["status"]
                if tag == "verified" and as_of is not None:
                    verified_at = e.get("verified_at")
                    if verified_at is None or verified_at > as_of:
                        # Trust-axis replay: the memory knew the VALUE by
                        # as_of (it passed the recorded_at check above), but
                        # verification either has no timestamp (unknown, so
                        # never assume it) or happened after as_of. Replay
                        # the honest state: asserted, not verified, no
                        # oracle. Storage is untouched; this is a read-time
                        # mask, same pattern as the audience scope filter.
                        tag = "asserted"
                if tag == "verified":
                    tag += f" ({e['evidence']})"
                actor_note = f" asserted_by={e.get('asserted_by', 'unknown')}"
                if tag.startswith("verified"):
                    actor_note += f" verified_by={e.get('verified_by', 'unknown')}"
                sources = e.get("source_episode_ids", [])
                source_note = (f" sources={','.join(sources)}" if sources else "")
                out.append(
                    f"fact.{cat}.{k}: {e['value']} [{tag}]"
                    f"{actor_note}{source_note}"
                )
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
        ok("stored fact names its asserting actor and authority",
           f["asserted_by"] == "agent:unspecified"
           and f["assertion_authority"] == "agent")

        try:
            mem.store_fact(
                "env", "bad_authority", "x",
                asserted_by="agent:test", assertion_authority="model",
            )
            ok("unknown assertion authority refused", False)
        except ValueError:
            ok("unknown assertion authority refused", True)

        try:
            mem.verify_fact(
                "env", "python", evidence="",
                verified_by="tool:ci", verification_authority="tool",
            )
            ok("empty evidence refused", False)
        except ValueError:
            ok("empty evidence refused", True)

        try:
            mem.verify_fact("env", "python", evidence="agent said so")
            ok("verification without a named verifier refused", False)
        except ValueError:
            ok("verification without a named verifier refused", True)

        try:
            mem.verify_fact(
                "env", "python", evidence="second agent repeated it",
                verified_by="agent:reviewer", verification_authority="agent",
            )
            ok("agent authority cannot promote a claim", False)
        except ValueError:
            ok("agent authority cannot promote a claim", True)

        mem.store_fact(
            "trust", "self_check", "v1",
            asserted_by="human:operator", assertion_authority="human",
        )
        try:
            mem.verify_fact(
                "trust", "self_check", evidence="I confirm my claim",
                verified_by="human:operator", verification_authority="human",
            )
            ok("an asserting actor cannot self-verify", False)
        except ValueError:
            ok("an asserting actor cannot self-verify", True)

        mem.verify_fact(
            "env", "python", evidence="ci run green on 3.8",
            verified_by="tool:ci", verification_authority="tool",
        )
        f = mem._read(mem.facts)["env"]["python"]
        ok("verification names its oracle", f["evidence"] == "ci run green on 3.8")
        ok("verify_fact stamps verified_at", f.get("verified_at") is not None)
        ok("verification names a distinct authority",
           f["verified_by"] == "tool:ci"
           and f["verification_authority"] == "tool")

        try:
            mem.verify_fact(
                "env", "missing", evidence="x",
                verified_by="tool:ci", verification_authority="tool",
            )
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

        # Provenance links: a derived fact can name the exact append-only
        # event that produced it, and a made-up handle is refused.
        source_id = mem.log_episode(
            "OBSERVED", "runtime reports Python 3.11", ["runtime"]
        )
        mem.store_fact(
            "env", "observed_python", "3.11",
            source_episode_ids=[source_id, source_id],
        )
        linked = mem._read(mem.facts)["env"]["observed_python"]
        ok("fact provenance keeps one stable source episode id",
           linked["source_episode_ids"] == [source_id])
        ok("context exposes the fact-to-episode provenance link",
           f"sources={source_id}" in mem.build_context())
        unknown_source_refused = False
        try:
            mem.store_fact(
                "env", "invented_source", "x",
                source_episode_ids=["episode-that-does-not-exist"],
            )
        except ValueError:
            unknown_source_refused = True
        ok("unknown source episode ids are refused",
           unknown_source_refused)

        # Retrieval fusion: a relevant older event must beat an irrelevant
        # newer one when the prompt budget admits only one episode. Both the
        # outcome and the action/tag lane point to the older event.
        mem.log_episode("MIGRATION", "schema flight completed", ["database"])
        mem.log_episode("CHAT", "unrelated newest event", ["general"])
        fused = mem.build_context("database migration schema", max_episodes=1)
        ok("multi-signal fusion beats recency-only retrieval",
           "schema flight completed" in fused
           and "unrelated newest event" not in fused)

        # Trust-axis replay: verification stamped after recorded_at must not
        # replay as verified for an as_of between the two (Atlas review,
        # 2026-08-10). Controlled timestamps, not real clock ticks, so the
        # gap is deterministic.
        mem.store_fact("trust", "claim", "v1")
        facts = mem._read(mem.facts)
        facts["trust"]["claim"]["recorded_at"] = 1000.0
        mem._write(mem.facts, facts)
        mem.verify_fact(
            "trust", "claim", evidence="human ruling",
            verified_by="human:reviewer", verification_authority="human",
        )
        facts = mem._read(mem.facts)
        facts["trust"]["claim"]["verified_at"] = 2000.0
        mem._write(mem.facts, facts)

        replay_before_recorded = mem.build_context(as_of=500.0)
        ok("as_of before recorded_at excludes the fact entirely",
           "fact.trust.claim" not in replay_before_recorded)

        replay_mid = mem.build_context(as_of=1500.0)
        ok("as_of between recorded_at and verified_at shows asserted, "
           "not verified (the oracle didn't exist yet)",
           "fact.trust.claim: v1 [asserted]" in replay_mid)
        ok("the replayed-asserted view carries no evidence string",
           "human ruling" not in replay_mid)

        replay_after = mem.build_context(as_of=2500.0)
        ok("as_of after verified_at shows the real verified status",
           "fact.trust.claim: v1 [verified (human ruling)]" in replay_after)

        current = mem.build_context()
        ok("no as_of set: current status shown regardless of when verified",
           "fact.trust.claim: v1 [verified (human ruling)]" in current)

        # Soft backfill: a fact verified before this fix has no verified_at
        # at all. The strict rule (missing = unknown = always downgrade)
        # would make old data look LESS trustworthy than it did before this
        # fix shipped. backfill_verified_at() sets verified_at = recorded_at
        # (best available signal) and tags the inference so it stays honest
        # about being an assumption, not an observation.
        mem.store_fact("trust", "legacy", "v1")
        facts = mem._read(mem.facts)
        facts["trust"]["legacy"]["recorded_at"] = 3000.0
        mem._write(mem.facts, facts)
        mem.verify_fact(
            "trust", "legacy", evidence="pre-fix ruling",
            verified_by="human:reviewer", verification_authority="human",
        )
        facts = mem._read(mem.facts)
        del facts["trust"]["legacy"]["verified_at"]  # simulate pre-fix data
        mem._write(mem.facts, facts)

        replay_no_backfill = mem.build_context(as_of=3000.0)
        ok("missing verified_at (unbackfilled) downgrades under any as_of",
           "fact.trust.legacy: v1 [asserted]" in replay_no_backfill)

        n = mem.backfill_verified_at()
        ok("backfill reports the count it touched", n == 1)
        f = mem._read(mem.facts)["trust"]["legacy"]
        ok("backfill sets verified_at = recorded_at",
           f["verified_at"] == f["recorded_at"] == 3000.0)
        ok("backfill tags the timestamp as inferred, not observed",
           f.get("verified_at_inferred") is True)

        replay_backfilled = mem.build_context(as_of=3000.0)
        ok("after backfill, old data replays verified at its own "
           "recorded_at (soft/lenient: no unearned regression)",
           "fact.trust.legacy: v1 [verified (pre-fix ruling)]"
           in replay_backfilled)

        n2 = mem.backfill_verified_at()
        ok("backfill is idempotent (a real verified_at is never touched)",
           n2 == 0)

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
        mem.verify_fact(
            "env", "python", "CI run 42",
            verified_by="tool:ci", verification_authority="tool",
        )
        mem.store_fact("env", "python", ">=3.11")
        kept = mem._read(mem.facts)["env"]["python"]
        ok("restating the same value keeps verified status and evidence",
           kept["status"] == "verified" and kept["evidence"] == "CI run 42")
        ok("restating the same value also keeps verified_at",
           kept.get("verified_at") is not None)
        corroborating = mem.log_episode(
            "OBSERVED", "second runtime check reports Python 3.11", ["runtime"]
        )
        mem.store_fact(
            "env", "python", ">=3.11",
            source_episode_ids=[corroborating],
        )
        enriched = mem._read(mem.facts)["env"]["python"]
        ok("same-value evidence accumulates without demoting the fact",
           enriched["status"] == "verified"
           and enriched["evidence"] == "CI run 42"
           and enriched["verified_by"] == "tool:ci"
           and enriched["verification_authority"] == "tool"
           and enriched["source_episode_ids"] == [corroborating])
        replacement_source = mem.log_episode(
            "OBSERVED", "runtime check reports Python 3.12", ["runtime"]
        )
        mem.store_fact(
            "env", "python", ">=3.12",
            source_episode_ids=[replacement_source],
        )
        eps4 = [json.loads(line) for line in
                mem.episodes.read_text().splitlines() if line.strip()]
        latest_supersession = [
            episode for episode in eps4
            if episode["action"] == "SUPERSEDED"
        ][-1]
        supersession_record = json.loads(latest_supersession["outcome"])
        ok("supersession preserves old and new provenance links",
           supersession_record["prior_source_episode_ids"] == [corroborating]
           and supersession_record["new_source_episode_ids"]
           == [replacement_source])

        # Contradiction proposals are read-only. Cheap deterministic cases
        # run before the evaluator, ambiguous cases fail to UNKNOWN, and even
        # a positive contradiction verdict remains a review proposal.
        mem.store_fact("policy", "term", "Fall", valid_from=10, valid_until=20)
        before_proposals = mem._read(mem.facts)
        exact_calls = []
        exact = mem.propose_contradiction(
            "policy", "term", "  fall  ", evaluator=lambda *_: exact_calls.append(1)
        )
        ok("normalized exact match proposes corroboration without evaluator",
           exact["outcome"] == "corroborate" and not exact_calls)
        historical = mem.propose_contradiction(
            "policy", "term", "Spring", valid_from=30, valid_until=40,
            evaluator=lambda *_: (_ for _ in ()).throw(RuntimeError("unused")),
        )
        ok("non-overlapping bounded windows coexist without evaluator",
           historical["outcome"] == "coexist"
           and historical["verdict"] == "compatible")
        ambiguous = mem.propose_contradiction("policy", "term", "Spring")
        ok("missing temporal evidence and evaluator stays unknown",
           ambiguous["outcome"] == "review"
           and ambiguous["verdict"] == "unknown")
        failed = mem.propose_contradiction(
            "policy", "term", "Spring",
            evaluator=lambda *_: (_ for _ in ()).throw(RuntimeError("offline")),
        )
        ok("evaluator failure stays unknown, never false",
           failed["verdict"] == "unknown"
           and "RuntimeError" in failed["reason"])
        malformed = mem.propose_contradiction(
            "policy", "term", "Spring", evaluator=lambda *_: {"verdict": "no"}
        )
        ok("malformed evaluator result stays unknown",
           malformed["verdict"] == "unknown")
        conflict = mem.propose_contradiction(
            "policy", "term", "Spring",
            evaluator=lambda *_: {"verdict": "contradiction",
                                  "reason": "same term, different label"},
        )
        ok("positive contradiction remains a review-only proposal",
           conflict["outcome"] == "review_replacement"
           and conflict["mutates"] is False)
        ok("contradiction proposals never change stored facts",
           mem._read(mem.facts) == before_proposals)

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

        # the alternative field: a rejection that names the better value
        # redirects the next session instead of dead-ending it
        mem.store_fact("env", "region", "us-east1")
        mem.reject_fact("env", "region", "us-east1",
                        "project runs in us-west2", alternative="us-west2")
        redirect_msg = ""
        try:
            mem.store_fact("env", "region", "us-east1")
        except ValueError as exc:
            redirect_msg = str(exc)
        ok("a tombstone with an alternative names it in the refusal",
           "Use instead: us-west2" in redirect_msg)
        ok("the alternative survives in the tombstone record",
           mem._read(mem.tombstones)["env/region"]["us-east1"]
           .get("alternative") == "us-west2")
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

        # valid-at: the world-time axis, distinct from learned-at
        mem.store_fact("policy", "gpa_floor", "3.5",
                       valid_from=100.0, valid_until=200.0)
        mem.store_fact("policy", "colors", "blue")  # unwindowed
        ctx_in = mem.build_context(valid_at=150.0)
        ctx_out = mem.build_context(valid_at=250.0)
        ok("a windowed fact appears inside its validity window",
           "gpa_floor" in ctx_in)
        ok("a windowed fact is excluded outside its window",
           "gpa_floor" not in ctx_out)
        ok("unwindowed facts are always included under valid-at",
           "colors" in ctx_out)
        ok("the valid-at header states the unwindowed limit",
           "unwindowed facts always included" in ctx_out.splitlines()[0])

        # scope-audience: the publication boundary, enforced at assembly
        mem.store_fact("kit", "license", "MIT", scope="public")
        mem.store_fact("ops", "roster_note", "counselor split", scope="regulated")
        pub = mem.build_context(audience="public")
        internal = mem.build_context(audience="internal")
        unfiltered = mem.build_context()
        ok("a public audience sees only public facts",
           "license" in pub and "roster_note" not in pub and "colors" not in pub)
        ok("pre-scope facts count as internal against a public audience",
           "fact.env.python" not in pub)
        ok("an internal audience excludes regulated",
           "roster_note" not in internal and "colors" in internal)
        ok("no audience means no scope filter",
           "roster_note" in unfiltered)
        bad_scope = False
        try:
            mem.store_fact("x", "y", "z", scope="secret")
        except ValueError:
            bad_scope = True
        ok("an unknown scope is refused", bad_scope)
        ok("audience filtering omits the unscoped episodic tier entirely",
           "episode:" not in pub and "episodes omitted" in pub.splitlines()[0])
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
