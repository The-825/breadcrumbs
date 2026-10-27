#!/usr/bin/env python3
"""Concept lineage v1: strict validator, pure projection and safe renderer.

Read-only and standard-library only (Python 3.9+). It validates one JSON graph
that links public source records to concepts and to consumer uses, derives
labelled counts, and renders a standalone page. It never opens a network
connection, executes source code, reads a clock or writes outside the path the
caller names. Labels describe supplied evidence, not independent authenticity,
release authority or adoption.

Usage:
    lineage.py validate GRAPH.json [--private]
    lineage.py project GRAPH.json [--input-manifest-sha256 HEX]
    lineage.py render PROJECTION.json [-o OUT.html]
    lineage.py demo GRAPH.json [-o OUT.html]   (project with the graph file digest, then render)
"""
from __future__ import annotations

import base64
import hashlib
import html
import json
import re
import sys
import unicodedata
from datetime import datetime
from urllib.parse import unquote

SCHEMA = "concept-lineage/1"
PROJECTION_SCHEMA = "concept-lineage-projection/1"

MAX_INPUT = 2 * 1024 * 1024
MAX_DEPTH = 12
MAX_STRING = 2048
MAX_ID = 180
MAX_HTML = 8 * 1024 * 1024
MAX_DIGITS = 16
LIMITS = {
    "sources": 500,
    "concepts": 500,
    "consumers": 100,
    "uses": 2000,
    "evidence": 2000,
    "refinements": 1000,
}

ID_PATTERN = (
    r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}/[A-Za-z0-9][A-Za-z0-9_.-]{0,63}:"
    r"(repository|research|candidate|pool|advisory|concept|consumer|use|evidence|refinement):"
    r"[A-Za-z0-9][A-Za-z0-9_.@/-]{0,95}"
)
_ID_RE = re.compile(ID_PATTERN)
_HEX40 = re.compile(r"[0-9a-f]{40}")
_HEX64 = re.compile(r"[0-9a-f]{64}")
_TS_RE = re.compile(
    r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d{1,6})?(Z|[+-](\d{2}):(\d{2}))"
)
_PATHLIKE = re.compile(r"(?:^|\s)(?:[A-Za-z]:[\\/]|[\\/]{2}|/(?:Users|home|tmp|etc|var|mnt|private)/)|^[\\/]")

SOURCE_KINDS = ("repository", "research", "candidate", "pool", "advisory")
EVIDENCE_DEPTHS = ("unverified", "readme-screened", "source-assessment")
RELATIONSHIPS = ("appraised_mechanism", "conceptual_similarity", "documented_origin")
VISIBILITIES = ("public", "synthetic", "private")
DECISIONS = ("proposed", "accepted", "rejected", "deferred")
EVIDENCE_KINDS = ("change", "synthetic_test", "merge", "deployment", "runtime")
UNKNOWN_REASONS = ("not_captured", "source_unavailable", "identity_unresolved", "consumer_unavailable")
MISSING_REASONS = (
    "not_captured",
    "receipt_absent",
    "consumer_unavailable",
    "source_unavailable",
    "identity_unresolved",
    "not_applicable",
)
APPROVED_HOSTS = ("github.com", "doi.org", "arxiv.org")
PUBLIC_CLASSES = ("public", "synthetic_public")
PRIVATE_CLASS = "private_metadata"

ENVELOPE_KEYS = {"schema_version", "data_class", "sources", "concepts", "consumers", "uses", "evidence", "refinements"}
SOURCE_KEYS = {
    "id", "owner", "record_kind", "record_id", "title", "url",
    "upstream_version", "catalog_revision", "aliases", "evidence_depth",
}
CONCEPT_KEYS = {"id", "owner", "title", "summary", "source_ids", "relationship", "origin_evidence_id"}
CONSUMER_KEYS = {"id", "owner", "title", "visibility"}
USE_KEYS = {
    "id", "concept_id", "consumer_id", "decision", "adaptation", "refinement",
    "source_versions_used", "evidence_ids",
}
USE_EVIDENCE_KEYS = {
    "id", "use_id", "consumer_id", "kind", "consumer_revision", "artifact_sha256",
    "result", "url", "observed_at", "missing_reason",
}
ORIGIN_EVIDENCE_KEYS = {
    "id", "kind", "concept_id", "source_id", "source_revision", "artifact_sha256",
    "result", "url", "observed_at", "missing_reason",
}
REFINEMENT_KEYS = {"id", "from_concept_id", "to_concept_id", "summary", "evidence_ids"}
VERSION_KEYS = {"kind", "value", "reason"}
PROJECTION_KEYS = {
    "schema_version", "input_manifest_sha256", "packet_sha256", "packet",
    "independent_authenticity_verified", "authority_granted",
}

BUCKETS = (
    "proposed",
    "accepted_without_observed_change",
    "accepted_with_observed_change",
    "rejected",
    "deferred",
)
ORIGIN_LABEL_DOCUMENTED = "Documented source (supplied evidence)"
ORIGIN_LABEL_UNRESOLVED = "Origin unresolved; not borrowed"
ORIGIN_LABEL_MECHANISM = "Appraised mechanism; origin not asserted"
REVISION_MATCH = "revision_match"
REVISION_CHANGED = "revision_changed_scope_unknown"
UNVERIFIED = "unverified"
TEST_MATCHED = "matched test pair"
TEST_UNMATCHED = "unmatched test revision"
TEST_NO_RECEIPT = "reported pass, receipt absent"
RELEASE_MATCH = "revision match only"
RELEASE_UNVERIFIED = "relation to change revision unverified"


class LineageError(ValueError):
    """Content-free failure: the message is only a stable code."""

    def __init__(self, code):
        ValueError.__init__(self, code)
        self.code = code


def fail(code):
    raise LineageError(code)


# ---------------------------------------------------------------- parsing


def _scan_depth(data):
    depth = 0
    in_str = False
    esc = False
    for b in data:
        if in_str:
            if esc:
                esc = False
            elif b == 0x5C:
                esc = True
            elif b == 0x22:
                in_str = False
            continue
        if b == 0x22:
            in_str = True
        elif b == 0x5B or b == 0x7B:
            depth += 1
            if depth > MAX_DEPTH:
                fail("too_deep")
        elif b == 0x5D or b == 0x7D:
            depth -= 1


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            fail("duplicate_key")
        out[key] = value
    return out


def _parse_int(text):
    if len(text.lstrip("-")) > MAX_DIGITS:
        fail("number_too_large")
    return int(text)


def _parse_float(text):
    if len(text) > 32:
        fail("number_too_large")
    value = float(text)
    if value != value or value in (float("inf"), float("-inf")):
        fail("nonfinite_number")
    return value


def _parse_constant(_name):
    fail("nonfinite_number")


def parse_json_bytes(data):
    if not isinstance(data, (bytes, bytearray)):
        fail("type")
    if len(data) > MAX_INPUT:
        fail("input_too_large")
    if data[:3] == b"\xef\xbb\xbf":
        fail("bom")
    try:
        text = bytes(data).decode("utf-8")
    except UnicodeDecodeError:
        fail("invalid_utf8")
    _scan_depth(bytes(data))
    try:
        return json.loads(
            text,
            object_pairs_hook=_pairs,
            parse_int=_parse_int,
            parse_float=_parse_float,
            parse_constant=_parse_constant,
        )
    except LineageError:
        raise
    except RecursionError:
        fail("too_deep")
    except ValueError:
        fail("invalid_json")


def canonical_bytes(obj):
    try:
        return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError):
        fail("not_canonical")


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def canonical_sha256(obj):
    return sha256_hex(canonical_bytes(obj))


# ---------------------------------------------------------------- field rules


def _obj(value, keys):
    if type(value) is not dict:
        fail("type")
    present = set(value)
    if present - keys:
        fail("unknown_field")
    if keys - present:
        fail("missing_field")
    return value


def _arr(value, limit=None):
    if type(value) is not list:
        fail("type")
    if limit is not None and len(value) > limit:
        fail("too_many")
    return value


def _text(value, nonempty=False, limit=MAX_STRING):
    if type(value) is not str:
        fail("type")
    if len(value) > limit:
        fail("too_long")
    if nonempty and not value:
        fail("empty")
    if unicodedata.normalize("NFC", value) != value:
        fail("not_nfc")
    for ch in value:
        if unicodedata.category(ch) in ("Cc", "Cf", "Zl", "Zp", "Cs", "Co", "Cn"):
            fail("bad_character")
    if value and _PATHLIKE.search(value):
        fail("path_like")
    return value


def _enum(value, allowed):
    if type(value) is not str or value not in allowed:
        fail("bad_enum")
    return value


def _id(value, kinds):
    if type(value) is not str or len(value) > MAX_ID:
        fail("bad_id")
    match = _ID_RE.fullmatch(value)
    if not match or match.group(1) not in kinds:
        fail("bad_id")
    for segment in value.split(":", 2)[2].split("/"):
        if segment in ("", ".", ".."):
            fail("bad_id")
    return value


def _kind_of(identifier):
    return identifier.split(":", 2)[1]


def _prefix_of(identifier):
    return identifier.split(":", 2)[0]


def _sha(value, nullable=False):
    if value is None and nullable:
        return None
    if type(value) is not str or not _HEX64.fullmatch(value):
        fail("bad_digest")
    return value


def _version(value):
    _obj(value, VERSION_KEYS)
    kind = value["kind"]
    if kind == "git":
        if type(value["value"]) is not str or not _HEX40.fullmatch(value["value"]) or value["reason"] is not None:
            fail("bad_version")
    elif kind == "publication":
        _text(value["value"], nonempty=True, limit=128)
        if value["reason"] is not None:
            fail("bad_version")
    elif kind == "unknown":
        if value["value"] is not None or _enum(value["reason"], UNKNOWN_REASONS) is None:
            fail("bad_version")
    else:
        fail("bad_version")
    return (kind, value["value"], value["reason"])


def _url(value):
    """Return (host, decoded path segments) for a safe approved HTTPS URL."""
    if type(value) is not str or not value or len(value) > MAX_STRING:
        fail("bad_url")
    for ch in value:
        if ord(ch) <= 0x20 or ord(ch) >= 0x7F or ch == "\\":
            fail("bad_url")
    if not value.startswith("https://"):
        fail("bad_url")
    rest = value[len("https://"):]
    if "?" in rest or "#" in rest:
        fail("bad_url")
    host, sep, path = rest.partition("/")
    if host not in APPROVED_HOSTS or not sep or not path:
        fail("bad_url")
    segments = []
    for raw in path.split("/"):
        if raw == "":
            fail("bad_url")
        decoded = raw
        for _ in range(3):
            nxt = unquote(decoded)
            if nxt == decoded:
                break
            decoded = nxt
        if decoded in (".", "..") or "/" in decoded or "\\" in decoded:
            fail("bad_url")
        if any(ord(c) < 0x20 or ord(c) == 0x7F for c in decoded):
            fail("bad_url")
        segments.append(raw)
    return host, segments


def _timestamp(value):
    if type(value) is not str:
        fail("bad_timestamp")
    match = _TS_RE.fullmatch(value)
    if not match:
        fail("bad_timestamp")
    try:
        datetime(*[int(match.group(i)) for i in range(1, 7)])
    except ValueError:
        fail("bad_timestamp")
    if match.group(8) is not None and (int(match.group(8)) > 23 or int(match.group(9)) > 59):
        fail("bad_timestamp")
    return value


def _common_receipt(row, revision):
    digest = _sha(row["artifact_sha256"], nullable=True)
    url = None if row["url"] is None else row["url"]
    if url is not None:
        _url(url)
    if row["observed_at"] is not None:
        _timestamp(row["observed_at"])
    reason = row["missing_reason"]
    if reason is not None:
        _enum(reason, MISSING_REASONS)
    needs_reason = digest is None or revision[0] == "unknown"
    if needs_reason != (reason is not None):
        fail("missing_reason")
    if url is not None and revision[0] == "unknown":
        fail("url_mismatch")
    return digest, url


def _commit_url(owner_repo, revision):
    return "https://github.com/%s/commit/%s" % (owner_repo, revision)


# ---------------------------------------------------------------- validation


def validate_graph(env, allow_private=False):
    """Validate a graph envelope. Returns an index dict; raises LineageError."""
    _obj(env, ENVELOPE_KEYS)
    if env["schema_version"] != SCHEMA:
        fail("schema_version")
    allowed_classes = PUBLIC_CLASSES + ((PRIVATE_CLASS,) if allow_private else ())
    data_class = _enum(env["data_class"], allowed_classes)
    arrays = {name: _arr(env[name], LIMITS[name]) for name in LIMITS}

    folded = {}

    def claim(identifier, code="duplicate_id"):
        key = identifier.casefold()
        if key in folded:
            fail(code)
        folded[key] = identifier

    sources, concepts, consumers, uses, evidence, refinements = {}, {}, {}, {}, {}, {}

    for row in arrays["sources"]:
        _obj(row, SOURCE_KEYS)
        sid = _id(row["id"], SOURCE_KINDS)
        if _enum(row["record_kind"], SOURCE_KINDS) != _kind_of(sid):
            fail("source_kind")
        _text(row["owner"], nonempty=True)
        _text(row["record_id"], nonempty=True)
        _text(row["title"], nonempty=True)
        _url(row["url"])
        _version(row["upstream_version"])
        _text(row["catalog_revision"], nonempty=True, limit=128)
        _enum(row["evidence_depth"], EVIDENCE_DEPTHS)
        claim(sid)
        sources[sid] = row
    for row in sources.values():
        for alias in _arr(row["aliases"], 50):
            claim(_id(alias, SOURCE_KINDS), "alias_conflict")

    for row in arrays["concepts"]:
        _obj(row, CONCEPT_KEYS)
        cid = _id(row["id"], ("concept",))
        _text(row["owner"], nonempty=True)
        _text(row["title"], nonempty=True)
        _text(row["summary"], nonempty=True)
        ids = _arr(row["source_ids"], LIMITS["sources"])
        if not ids or len(set(ids)) != len(ids):
            fail("bad_source_ids")
        for sid in ids:
            _id(sid, SOURCE_KINDS)
            if sid not in sources:
                fail("unresolved_reference")
        _enum(row["relationship"], RELATIONSHIPS)
        if row["origin_evidence_id"] is not None:
            _id(row["origin_evidence_id"], ("evidence",))
        claim(cid)
        concepts[cid] = row

    for row in arrays["consumers"]:
        _obj(row, CONSUMER_KEYS)
        kid = _id(row["id"], ("consumer",))
        _text(row["owner"], nonempty=True)
        _text(row["title"], nonempty=True)
        visibility = _enum(row["visibility"], VISIBILITIES)
        if visibility == "private" and data_class in PUBLIC_CLASSES:
            fail("private_in_public")
        claim(kid)
        consumers[kid] = row

    for row in arrays["uses"]:
        _obj(row, USE_KEYS)
        uid = _id(row["id"], ("use",))
        _id(row["concept_id"], ("concept",))
        _id(row["consumer_id"], ("consumer",))
        _enum(row["decision"], DECISIONS)
        _text(row["adaptation"])
        _text(row["refinement"])
        _obj_map = row["source_versions_used"]
        if type(_obj_map) is not dict:
            fail("type")
        for key, version in _obj_map.items():
            _id(key, SOURCE_KINDS)
            _version(version)
        ev_ids = _arr(row["evidence_ids"], LIMITS["evidence"])
        for eid in ev_ids:
            _id(eid, ("evidence",))
        if len(set(ev_ids)) != len(ev_ids):
            fail("duplicate_evidence_id")
        claim(uid)
        uses[uid] = row

    for row in arrays["evidence"]:
        if type(row) is not dict:
            fail("type")
        if row.get("kind") == "origin":
            _obj(row, ORIGIN_EVIDENCE_KEYS)
            _id(row["concept_id"], ("concept",))
            _id(row["source_id"], SOURCE_KINDS)
            revision = _version(row["source_revision"])
            _enum(row["result"], ("observed", "unknown"))
        else:
            _obj(row, USE_EVIDENCE_KEYS)
            _id(row["use_id"], ("use",))
            _id(row["consumer_id"], ("consumer",))
            kind = _enum(row["kind"], EVIDENCE_KINDS)
            revision = _version(row["consumer_revision"])
            _enum(row["result"], ("pass", "fail", "unknown") if kind == "synthetic_test" else ("observed", "unknown"))
        eid = _id(row["id"], ("evidence",))
        _common_receipt(row, revision)
        claim(eid)
        evidence[eid] = row

    for row in arrays["refinements"]:
        _obj(row, REFINEMENT_KEYS)
        rid = _id(row["id"], ("refinement",))
        _id(row["from_concept_id"], ("concept",))
        _id(row["to_concept_id"], ("concept",))
        _text(row["summary"], nonempty=True)
        ev_ids = _arr(row["evidence_ids"], LIMITS["evidence"])
        for eid in ev_ids:
            _id(eid, ("evidence",))
        if len(set(ev_ids)) != len(ev_ids):
            fail("duplicate_evidence_id")
        claim(rid)
        refinements[rid] = row

    # --- cross references ---
    pair_seen = set()
    use_rows = {uid: set() for uid in uses}
    for eid, row in evidence.items():
        if row["kind"] == "origin":
            continue
        use = uses.get(row["use_id"])
        if use is None:
            fail("orphan_evidence")
        if row["consumer_id"] != use["consumer_id"]:
            fail("evidence_consumer_mismatch")
        use_rows[row["use_id"]].add(eid)
        if row["url"] is not None:
            revision = _version(row["consumer_revision"])
            if revision[0] != "git":
                fail("url_mismatch")
            if row["url"] != _commit_url(_prefix_of(use["consumer_id"]), revision[1]):
                fail("url_mismatch")

    for uid, use in uses.items():
        concept = concepts.get(use["concept_id"])
        if concept is None or use["consumer_id"] not in consumers:
            fail("unresolved_reference")
        pair = (use["concept_id"], use["consumer_id"])
        if pair in pair_seen:
            fail("duplicate_use")
        pair_seen.add(pair)
        if set(use["source_versions_used"]) != set(concept["source_ids"]):
            fail("source_versions_mismatch")
        for eid in use["evidence_ids"]:
            row = evidence.get(eid)
            if row is None or row["kind"] == "origin":
                fail("evidence_binding")
        if set(use["evidence_ids"]) != use_rows[uid]:
            fail("evidence_binding")

    for cid, concept in concepts.items():
        origin_id = concept["origin_evidence_id"]
        if concept["relationship"] != "documented_origin":
            if origin_id is not None:
                fail("origin_not_allowed")
            continue
        row = evidence.get(origin_id) if origin_id is not None else None
        if row is None or row["kind"] != "origin":
            fail("origin_missing")
        _check_origin(concept, row, sources)

    for eid, row in evidence.items():
        if row["kind"] != "origin":
            continue
        concept = concepts.get(row["concept_id"])
        if concept is None or concept["origin_evidence_id"] != eid:
            fail("origin_unreferenced")
        if row["source_id"] not in concept["source_ids"]:
            fail("origin_source_mismatch")

    edges = {}
    for row in refinements.values():
        src, dst = row["from_concept_id"], row["to_concept_id"]
        if src not in concepts or dst not in concepts:
            fail("unresolved_reference")
        if src == dst:
            fail("self_refinement")
        for eid in row["evidence_ids"]:
            ev = evidence.get(eid)
            if ev is None:
                fail("unresolved_reference")
            concept_id = ev["concept_id"] if ev["kind"] == "origin" else uses[ev["use_id"]]["concept_id"]
            if concept_id not in (src, dst):
                fail("unrelated_evidence")
        edges.setdefault(src, []).append(dst)
    _require_acyclic(edges)

    return {
        "data_class": data_class,
        "sources": sources,
        "concepts": concepts,
        "consumers": consumers,
        "uses": uses,
        "evidence": evidence,
        "refinements": refinements,
    }


def _check_origin(concept, row, sources):
    if row["concept_id"] != _concept_id_of(concept):
        fail("origin_unreferenced")
    if row["source_id"] not in concept["source_ids"]:
        fail("origin_source_mismatch")
    revision = _version(row["source_revision"])
    if row["result"] != "observed" or row["artifact_sha256"] is None or revision[0] == "unknown" or row["url"] is None:
        fail("origin_incomplete")
    source = sources[row["source_id"]]
    _host, source_segments = _url(source["url"])
    if revision[0] == "git":
        if _host != "github.com" or len(source_segments) < 2:
            fail("origin_url_mismatch")
        repo = "%s/%s" % (source_segments[0], source_segments[1])
        if row["url"] != _commit_url(repo, revision[1]):
            fail("origin_url_mismatch")
    else:
        declared = _version(source["upstream_version"])
        if declared[0] != "publication" or declared[1] != revision[1] or row["url"] != source["url"]:
            fail("origin_url_mismatch")


def _concept_id_of(concept):
    return concept["id"]


def _require_acyclic(edges):
    state = {}
    for start in sorted(edges):
        if state.get(start):
            continue
        stack = [(start, iter(edges.get(start, ())))]
        state[start] = 1
        while stack:
            node, children = stack[-1]
            advanced = False
            for child in children:
                if state.get(child) == 1:
                    fail("derivation_cycle")
                if not state.get(child):
                    state[child] = 1
                    stack.append((child, iter(edges.get(child, ()))))
                    advanced = True
                    break
            if not advanced:
                state[node] = 2
                stack.pop()


# ---------------------------------------------------------------- projection


def _version_label(version):
    kind, value, reason = _version(version)
    if kind == "git":
        return "git:" + value[:12]
    if kind == "publication":
        return "publication:" + value
    return "unknown:" + reason


def _freshness(current, used):
    cur, old = _version(current), _version(used)
    if cur[0] == "unknown" or old[0] == "unknown" or cur[0] != old[0]:
        return UNVERIFIED
    return REVISION_MATCH if cur[1] == old[1] else REVISION_CHANGED


def _derive_use(use, rows, concept, consumer, sources):
    changes, tests, releases, incomplete = [], [], [], 0
    change_revs = set()
    for row in rows:
        revision = _version(row["consumer_revision"])
        if row["kind"] == "change":
            if row["result"] == "observed" and revision[0] == "git" and row["artifact_sha256"] is not None:
                change_revs.add(revision[1])
                changes.append({"id": row["id"], "revision": revision[1]})
            else:
                incomplete += 1
    matched = set()
    for row in rows:
        revision = _version(row["consumer_revision"])
        if row["kind"] == "synthetic_test":
            if row["result"] == "pass":
                if row["artifact_sha256"] is None or revision[0] != "git":
                    status = TEST_NO_RECEIPT
                elif revision[1] in change_revs:
                    status = TEST_MATCHED
                    matched.add(revision[1])
                else:
                    status = TEST_UNMATCHED
            else:
                status = row["result"]
            tests.append({"id": row["id"], "revision": _version_label(row["consumer_revision"]), "result": row["result"], "status": status})
        elif row["kind"] in ("merge", "deployment", "runtime"):
            relation = RELEASE_MATCH if revision[0] == "git" and revision[1] in change_revs else RELEASE_UNVERIFIED
            releases.append({"id": row["id"], "kind": row["kind"], "revision": _version_label(row["consumer_revision"]), "result": row["result"], "relation": relation})
    passing = any(t["result"] == "pass" for t in tests)
    failing = any(t["result"] == "fail" for t in tests)
    if use["decision"] == "accepted":
        bucket = "accepted_with_observed_change" if changes else "accepted_without_observed_change"
    else:
        bucket = use["decision"]
    return {
        "use_id": use["id"],
        "consumer_id": consumer["id"],
        "consumer_title": consumer["title"],
        "decision": use["decision"],
        "bucket": bucket,
        "adaptation": use["adaptation"],
        "refinement": use["refinement"],
        "changes": changes,
        "incomplete_change_receipts": incomplete,
        "tests": tests,
        "matched_test_pairs": len(matched),
        "changes_without_matching_validation": len([c for c in changes if c["revision"] not in matched]),
        "validation_mixed": passing and failing,
        "releases": releases,
        "freshness": [
            {
                "source_id": sid,
                "used": _version_label(use["source_versions_used"][sid]),
                "current": _version_label(sources[sid]["upstream_version"]),
                "status": _freshness(sources[sid]["upstream_version"], use["source_versions_used"][sid]),
            }
            for sid in concept["source_ids"]
        ],
    }


def derive(env, allow_private=False):
    """Pure deterministic view of a graph; no clock, no network."""
    idx = validate_graph(env, allow_private=allow_private)
    use_rows = {}
    for eid in sorted(idx["evidence"]):
        row = idx["evidence"][eid]
        if row["kind"] != "origin":
            use_rows.setdefault(row["use_id"], []).append(row)
    concept_uses = {}
    for uid in sorted(idx["uses"]):
        concept_uses.setdefault(idx["uses"][uid]["concept_id"], []).append(idx["uses"][uid])
    refined_from, refines = {}, {}
    for row in idx["refinements"].values():
        refines.setdefault(row["from_concept_id"], []).append(row["to_concept_id"])
        refined_from.setdefault(row["to_concept_id"], []).append(row["from_concept_id"])
    concept_views = []
    totals = {name: 0 for name in BUCKETS}
    for cid in sorted(idx["concepts"]):
        concept = idx["concepts"][cid]
        rel = concept["relationship"]
        label = {
            "documented_origin": ORIGIN_LABEL_DOCUMENTED,
            "conceptual_similarity": ORIGIN_LABEL_UNRESOLVED,
            "appraised_mechanism": ORIGIN_LABEL_MECHANISM,
        }[rel]
        origin = None
        if rel == "documented_origin":
            row = idx["evidence"][concept["origin_evidence_id"]]
            origin = {
                "id": row["id"],
                "source_id": row["source_id"],
                "revision": _version_label(row["source_revision"]),
                "url": row["url"],
                "artifact_sha256": row["artifact_sha256"],
            }
        buckets = {name: 0 for name in BUCKETS}
        use_views = []
        for use in concept_uses.get(cid, ()):
            view = _derive_use(use, use_rows.get(use["id"], []), concept, idx["consumers"][use["consumer_id"]], idx["sources"])
            buckets[view["bucket"]] += 1
            totals[view["bucket"]] += 1
            use_views.append(view)
        concept_views.append({
            "id": cid,
            "title": concept["title"],
            "summary": concept["summary"],
            "relationship": rel,
            "origin_label": label,
            "origin": origin,
            "sources": [
                {
                    "id": sid,
                    "title": idx["sources"][sid]["title"],
                    "url": idx["sources"][sid]["url"],
                    "evidence_depth": idx["sources"][sid]["evidence_depth"],
                    "version": _version_label(idx["sources"][sid]["upstream_version"]),
                }
                for sid in concept["source_ids"]
            ],
            "buckets": buckets,
            "uses": use_views,
            "refines": sorted(refines.get(cid, [])),
            "refined_from": sorted(refined_from.get(cid, [])),
        })
    return {
        "data_class": idx["data_class"],
        "source_count": len(idx["sources"]),
        "sources": [
            {"id": sid, "title": idx["sources"][sid]["title"], "url": idx["sources"][sid]["url"],
             "evidence_depth": idx["sources"][sid]["evidence_depth"],
             "version": _version_label(idx["sources"][sid]["upstream_version"])}
            for sid in sorted(idx["sources"])
        ],
        "concepts": concept_views,
        "totals": totals,
    }


def build_projection(packet, input_manifest_sha256):
    validate_graph(packet)
    _sha(input_manifest_sha256)
    return {
        "schema_version": PROJECTION_SCHEMA,
        "input_manifest_sha256": input_manifest_sha256,
        "packet_sha256": canonical_sha256(packet),
        "packet": packet,
        "independent_authenticity_verified": False,
        "authority_granted": False,
    }


def validate_projection(projection):
    _obj(projection, PROJECTION_KEYS)
    if projection["schema_version"] != PROJECTION_SCHEMA:
        fail("schema_version")
    _sha(projection["input_manifest_sha256"])
    _sha(projection["packet_sha256"])
    if projection["independent_authenticity_verified"] is not False or projection["authority_granted"] is not False:
        fail("authority_flags")
    validate_graph(projection["packet"])
    if canonical_sha256(projection["packet"]) != projection["packet_sha256"]:
        fail("packet_digest")
    return projection


# ---------------------------------------------------------------- rendering

_CSS = (
    "body{font:16px/1.5 system-ui,sans-serif;margin:1rem auto;max-width:72rem;padding:0 1rem;color:#111;background:#fff}"
    "h1,h2{line-height:1.2}"
    ".scroll{overflow-x:auto}"
    "table{border-collapse:collapse;width:100%}"
    "th,td{border:1px solid #555;padding:.35rem .5rem;text-align:left;vertical-align:top}"
    "th{background:#eee}"
    "a:focus-visible,button:focus-visible,input:focus-visible,.scroll:focus-visible,summary:focus-visible"
    "{outline:3px solid #0050c8;outline-offset:2px}"
    ".note{border-left:4px solid #555;padding-left:.75rem}"
    "[hidden]{display:none}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}"
)

_JS = (
    "(function(){"
    "var d=JSON.parse(document.getElementById('lineage-data').textContent);"
    "var q=document.getElementById('filter'),tb=document.getElementById('use-table');"
    "var gv=document.getElementById('graph-view'),tv=document.getElementById('table-view');"
    "var btn=document.getElementById('toggle');"
    "function el(t,x){var e=document.createElement(t);if(x!==undefined){e.textContent=x}return e}"
    "function build(){gv.textContent='';if(!d.concepts.length){gv.appendChild(el('p','No concepts recorded.'));return}"
    "var ul=el('ul');d.concepts.forEach(function(c){var li=el('li',c.title+' ('+c.origin_label+')');"
    "var s=el('ul');c.sources.forEach(function(x){s.appendChild(el('li','Source: '+x.title+' ['+x.version+']'))});"
    "c.uses.forEach(function(u){s.appendChild(el('li','Consumer: '+u.consumer_title+', decision '+u.decision+', '+u.bucket.split('_').join(' ')))});"
    "c.refines.forEach(function(r){s.appendChild(el('li','Refines into: '+r))});"
    "li.appendChild(s);ul.appendChild(li)});gv.appendChild(ul)}"
    "build();"
    "q.addEventListener('input',function(){var v=q.value.toLowerCase();"
    "Array.prototype.forEach.call(tb.tBodies[0].rows,function(r){r.hidden=v&&r.textContent.toLowerCase().indexOf(v)<0})});"
    "btn.addEventListener('click',function(){var g=gv.hidden;gv.hidden=!g;tv.hidden=g;"
    "btn.textContent=g?'Show list view':'Show graph view'});"
    "})();"
)


def _esc(value):
    return html.escape(str(value), quote=True)


def _json_for_script(obj):
    text = json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def _link(url, text):
    return '<a href="%s" rel="noopener noreferrer">%s</a>' % (_esc(url), _esc(text))


def _use_cells(concept, use):
    changes = ", ".join(c["revision"][:12] for c in use["changes"]) or "none supplied"
    validation = "; ".join("%s (%s)" % (t["status"], t["revision"]) for t in use["tests"]) or "no test receipt"
    validation += "; matched pairs: %d; changes without matching validation: %d" % (
        use["matched_test_pairs"], use["changes_without_matching_validation"])
    if use["validation_mixed"]:
        validation += "; mixed pass and fail receipts"
    releases = "; ".join("%s %s (%s)" % (r["kind"], r["revision"], r["relation"]) for r in use["releases"]) or "none supplied"
    fresh = "; ".join("%s: %s" % (f["source_id"].rsplit(":", 1)[-1], f["status"]) for f in use["freshness"])
    return [_esc(use["consumer_title"]), _esc(use["decision"]), _esc(use["bucket"].replace("_", " ")),
            _esc(changes), _esc(validation), _esc(releases), _esc(fresh)]


def render_html(projection):
    """Render a validated projection as one standalone, script-contained page."""
    validate_projection(projection)
    view = derive(projection["packet"])
    rows = []
    for concept in view["concepts"]:
        head = [_esc(concept["title"]), _esc(concept["origin_label"]),
                ", ".join(_link(s["url"], s["title"]) + " " + _esc(s["version"]) for s in concept["sources"])]
        if concept["uses"]:
            for use in concept["uses"]:
                rows.append(head + _use_cells(concept, use))
        else:
            rows.append(head + ["No consumer use recorded", "", "", "", "", "", ""])
    if rows:
        body_rows = "".join("<tr>" + "".join("<td>%s</td>" % c for c in r) + "</tr>" for r in rows)
    else:
        body_rows = '<tr><td colspan="10">No concepts recorded.</td></tr>'
    count_rows = "".join(
        "<tr><td>%s</td>%s</tr>" % (_esc(c["title"]), "".join("<td>%d</td>" % c["buckets"][b] for b in BUCKETS))
        for c in view["concepts"]
    ) or '<tr><td colspan="6">No concepts recorded.</td></tr>'
    source_rows = "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            _esc(s["title"]), _esc(s["evidence_depth"]), _esc(s["version"]), _link(s["url"], s["url"]))
        for s in view["sources"]
    ) or '<tr><td colspan="4">No sources recorded.</td></tr>'
    css_hash = base64.b64encode(hashlib.sha256(_CSS.encode("utf-8")).digest()).decode("ascii")
    js_hash = base64.b64encode(hashlib.sha256(_JS.encode("utf-8")).digest()).decode("ascii")
    csp = ("default-src 'none'; script-src 'sha256-%s'; style-src 'sha256-%s'; connect-src 'none'; "
           "base-uri 'none'; form-action 'none'" % (js_hash, css_hash))
    head_cols = ["Concept", "Origin", "Sources", "Consumer", "Decision", "Bucket", "Observed change",
                 "Validation", "Release receipts", "Source freshness"]
    page = "".join([
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">",
        "<meta http-equiv=\"Content-Security-Policy\" content=\"%s\">" % _esc(csp),
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">",
        "<title>Concept lineage</title><style>", _CSS, "</style></head><body>",
        "<h1>Concept lineage</h1>",
        "<p class=\"note\">Read-only view of supplied records. Labels describe supplied evidence, not independent "
        "authenticity, release authority or adoption. Source quality, local fit, decision, validation and observed "
        "benefit stay separate; there is no blended score. Packet digest: %s.</p>" % _esc(projection["packet_sha256"]),
        "<p><button id=\"toggle\" type=\"button\">Show graph view</button> ",
        "<label>Filter rows <input id=\"filter\" type=\"search\"></label></p>",
        "<div id=\"table-view\"><h2>Concept uses</h2><div class=\"scroll\" tabindex=\"0\" role=\"region\" aria-label=\"Concept uses\">",
        "<table id=\"use-table\"><thead><tr>", "".join("<th scope=\"col\">%s</th>" % h for h in head_cols),
        "</tr></thead><tbody>", body_rows, "</tbody></table></div></div>",
        "<div id=\"graph-view\" hidden></div>",
        "<h2>Consumers per decision bucket</h2><div class=\"scroll\" tabindex=\"0\" role=\"region\" aria-label=\"Bucket counts\"><table><thead><tr><th scope=\"col\">Concept</th>",
        "".join("<th scope=\"col\">%s</th>" % _esc(b.replace("_", " ")) for b in BUCKETS),
        "</tr></thead><tbody>", count_rows, "</tbody></table></div>",
        "<h2>Sources</h2><div class=\"scroll\" tabindex=\"0\" role=\"region\" aria-label=\"Sources\"><table><thead><tr>",
        "<th scope=\"col\">Source</th><th scope=\"col\">Evidence depth</th><th scope=\"col\">Version</th><th scope=\"col\">Link</th>",
        "</tr></thead><tbody>", source_rows, "</tbody></table></div>",
        "<script type=\"application/json\" id=\"lineage-data\">", _json_for_script(view), "</script>",
        "<script>", _JS, "</script></body></html>\n",
    ])
    if len(page.encode("utf-8")) > MAX_HTML:
        fail("html_too_large")
    return page


# ---------------------------------------------------------------- CLI


def read_file(path):
    with open(path, "rb") as handle:
        data = handle.read(MAX_INPUT + 1)
    return data


def _write(data):
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()


def main(argv):
    args = list(argv[1:])
    try:
        if len(args) >= 2 and args[0] == "validate":
            idx = validate_graph(parse_json_bytes(read_file(args[1])), allow_private="--private" in args[2:])
            _write(("valid sources=%d concepts=%d consumers=%d uses=%d\n" % (
                len(idx["sources"]), len(idx["concepts"]), len(idx["consumers"]), len(idx["uses"]))).encode("ascii"))
            return 0
        if len(args) >= 2 and args[0] == "project":
            digest = None
            if "--input-manifest-sha256" in args:
                digest = args[args.index("--input-manifest-sha256") + 1]
            data = read_file(args[1])
            if digest is None:
                digest = sha256_hex(data)
            _write(canonical_bytes(build_projection(parse_json_bytes(data), digest)))
            return 0
        if len(args) >= 2 and args[0] == "demo":
            data = read_file(args[1])
            page = render_html(build_projection(parse_json_bytes(data), sha256_hex(data)))
            if "-o" in args:
                with open(args[args.index("-o") + 1], "wb") as handle:
                    handle.write(page.encode("utf-8"))
            else:
                _write(page.encode("utf-8"))
            return 0
        if len(args) >= 2 and args[0] == "render":
            page = render_html(parse_json_bytes(read_file(args[1])))
            if "-o" in args:
                with open(args[args.index("-o") + 1], "wb") as handle:
                    handle.write(page.encode("utf-8"))
            else:
                _write(page.encode("utf-8"))
            return 0
    except LineageError as exc:
        sys.stderr.write("invalid: %s\n" % exc.code)
        return 2
    except (OSError, IndexError):
        sys.stderr.write("invalid: io_error\n")
        return 2
    sys.stderr.write(__doc__ or "")
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
