import base64
import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("lineage", HERE / "lineage.py")
lineage = importlib.util.module_from_spec(spec)
sys.modules["lineage"] = lineage
spec.loader.exec_module(lineage)

P = "example/lineage-demo:"
A = P + "repository:alpha"
PAPER = P + "research:paper1"
RETRY = P + "concept:retry-ledger"
CITE = P + "concept:citation-gate"


def load():
    return json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))


def row(env, key, ident):
    return next(r for r in env[key] if r["id"] == ident)


def code(env, **kw):
    try:
        lineage.validate_graph(env, **kw)
    except lineage.LineageError as exc:
        return exc.code
    return None


def git(ch):
    return {"kind": "git", "value": ch * 40, "reason": None}


class ParsingTests(unittest.TestCase):
    def parse(self, data):
        try:
            lineage.parse_json_bytes(data)
        except lineage.LineageError as exc:
            return exc.code

    def test_fixture_parses(self):
        self.assertIsNone(self.parse((HERE / "fixture.json").read_bytes()))

    def test_bom_and_utf8(self):
        self.assertEqual(self.parse(b"\xef\xbb\xbf{}"), "bom")
        self.assertEqual(self.parse(b"\xff\xfe{}"), "invalid_utf8")

    def test_duplicate_nonfinite_and_big_numbers(self):
        self.assertEqual(self.parse(b'{"a":1,"a":2}'), "duplicate_key")
        self.assertEqual(self.parse(b'{"a":NaN}'), "nonfinite_number")
        self.assertEqual(self.parse(b'{"a":Infinity}'), "nonfinite_number")
        self.assertEqual(self.parse(b'{"a":' + b"9" * 400 + b"}"), "number_too_large")
        self.assertEqual(self.parse(b'{"a":1e999}'), "nonfinite_number")

    def test_depth_and_size(self):
        self.assertEqual(self.parse(b"[" * 13 + b"]" * 13), "too_deep")
        self.assertIsNone(self.parse(b"[" * 12 + b"]" * 12))
        self.assertIn(self.parse(b"[" * (2 * 1024 * 1024)), ("too_deep", "input_too_large"))
        self.assertEqual(self.parse(b" " * (2 * 1024 * 1024 + 1)), "input_too_large")
        self.assertEqual(self.parse(b"{"), "invalid_json")


class FixtureTests(unittest.TestCase):
    def test_valid_and_deterministic(self):
        env = load()
        self.assertIsNone(code(env))
        self.assertEqual(lineage.derive(env), lineage.derive(copy.deepcopy(env)))
        self.assertEqual(lineage.canonical_bytes(env), lineage.canonical_bytes(copy.deepcopy(env)))

    def assert_equivalent_artifacts(self, first, second):
        self.assertEqual(lineage.derive(first), lineage.derive(second))
        left = lineage.build_projection(first, "1" * 64)
        right = lineage.build_projection(second, "1" * 64)
        self.assertEqual(left["packet_sha256"], right["packet_sha256"])
        self.assertEqual(lineage.canonical_bytes(left), lineage.canonical_bytes(right))
        self.assertEqual(lineage.render_html(left), lineage.render_html(right))

    def test_permuted_records_have_identical_artifacts(self):
        env = load()
        permuted = copy.deepcopy(env)
        for name in lineage.LIMITS:
            permuted[name].reverse()
        self.assert_equivalent_artifacts(env, permuted)

    def test_permuted_references_have_identical_artifacts(self):
        env = load()
        row(env, "sources", A)["aliases"] = [P + "repository:old-z", P + "repository:old-a"]
        row(env, "concepts", RETRY)["source_ids"].append(PAPER)
        for use in env["uses"]:
            if use["concept_id"] == RETRY:
                use["source_versions_used"][PAPER] = copy.deepcopy(row(env, "sources", PAPER)["upstream_version"])
        retry_use = next(use for use in env["uses"] if use["concept_id"] == RETRY and len(use["evidence_ids"]) > 1)
        env["refinements"].append({"id": P + "refinement:retry-citation", "from_concept_id": RETRY,
                                   "to_concept_id": CITE, "summary": "Fictional derivation",
                                   "evidence_ids": list(retry_use["evidence_ids"])})
        permuted = copy.deepcopy(env)
        for name, field in (("sources", "aliases"), ("concepts", "source_ids"),
                            ("uses", "evidence_ids"), ("refinements", "evidence_ids")):
            for record in permuted[name]:
                record[field].reverse()
        self.assert_equivalent_artifacts(env, permuted)

    def test_normalization_preserves_input_and_ordered_text(self):
        env = load()
        use = env["uses"][0]
        use["adaptation"] = "First step, then second step."
        before = copy.deepcopy(env)
        normalized = lineage.normalize_packet(env)
        self.assertEqual(env, before)
        self.assertEqual(row(normalized, "uses", use["id"])["adaptation"], use["adaptation"])
        invalid = copy.deepcopy(env)
        invalid["concepts"][0]["source_ids"] *= 2
        with self.assertRaises(lineage.LineageError):
            lineage.normalize_packet(invalid)

    def test_distinct_bucket_counts(self):
        view = lineage.derive(load())
        retry = next(c for c in view["concepts"] if c["id"] == RETRY)
        self.assertEqual(retry["buckets"], {
            "proposed": 1, "accepted_without_observed_change": 1, "accepted_with_observed_change": 2,
            "rejected": 0, "deferred": 0})
        cite = next(c for c in view["concepts"] if c["id"] == CITE)
        self.assertEqual((cite["buckets"]["deferred"], cite["buckets"]["rejected"]), (1, 1))

    def test_tested_untested_and_squash(self):
        view = lineage.derive(load())
        retry = next(c for c in view["concepts"] if c["id"] == RETRY)
        one = next(u for u in retry["uses"] if u["consumer_id"].endswith("one"))
        self.assertEqual(one["matched_test_pairs"], 1)
        self.assertEqual(one["changes_without_matching_validation"], 1)
        self.assertEqual(one["releases"][0]["relation"], lineage.RELEASE_UNVERIFIED)
        two = next(u for u in retry["uses"] if u["consumer_id"].endswith("two"))
        self.assertEqual((two["matched_test_pairs"], two["changes_without_matching_validation"]), (0, 1))
        three = next(u for u in retry["uses"] if u["consumer_id"].endswith("three"))
        self.assertEqual(three["bucket"], "proposed")

    def test_release_revision_match_only(self):
        env = load()
        row(env, "evidence", P + "evidence:m1")["consumer_revision"] = git("4")
        view = lineage.derive(env)
        one = next(u for c in view["concepts"] if c["id"] == RETRY for u in c["uses"] if u["consumer_id"].endswith("one"))
        self.assertEqual(one["releases"][0]["relation"], lineage.RELEASE_MATCH)

    def test_unmatched_and_receipt_absent_tests(self):
        env = load()
        row(env, "evidence", P + "evidence:t1")["consumer_revision"] = git("a")
        view = lineage.derive(env)
        one = next(u for c in view["concepts"] if c["id"] == RETRY for u in c["uses"] if u["consumer_id"].endswith("one"))
        self.assertEqual(one["tests"][0]["status"], lineage.TEST_UNMATCHED)
        self.assertEqual(one["matched_test_pairs"], 0)
        env = load()
        t = row(env, "evidence", P + "evidence:t1")
        t["artifact_sha256"], t["missing_reason"] = None, "receipt_absent"
        view = lineage.derive(env)
        one = next(u for c in view["concepts"] if c["id"] == RETRY for u in c["uses"] if u["consumer_id"].endswith("one"))
        self.assertEqual(one["tests"][0]["status"], lineage.TEST_NO_RECEIPT)

    def test_mixed_results_stay_visible(self):
        env = load()
        extra = copy.deepcopy(row(env, "evidence", P + "evidence:t1"))
        extra["id"] = P + "evidence:t2"
        extra["result"] = "fail"
        env["evidence"].append(extra)
        row(env, "uses", P + "use:retry-one")["evidence_ids"].append(extra["id"])
        one = next(u for c in lineage.derive(env)["concepts"] if c["id"] == RETRY for u in c["uses"] if u["consumer_id"].endswith("one"))
        self.assertTrue(one["validation_mixed"])

    def test_freshness_labels(self):
        view = lineage.derive(load())
        retry = next(c for c in view["concepts"] if c["id"] == RETRY)
        by_consumer = {u["consumer_id"].rsplit(":", 1)[1]: u["freshness"][0]["status"] for u in retry["uses"]}
        self.assertEqual(by_consumer["one"], lineage.REVISION_CHANGED)
        self.assertEqual(by_consumer["two"], lineage.REVISION_MATCH)
        env = load()
        row(env, "uses", P + "use:cite-one")["source_versions_used"][PAPER] = git("1")
        cite = next(c for c in lineage.derive(env)["concepts"] if c["id"] == CITE)
        self.assertEqual(cite["uses"][0]["freshness"][0]["status"], lineage.UNVERIFIED)

    def test_origin_labels(self):
        labels = {c["id"].rsplit(":", 1)[1]: c["origin_label"] for c in lineage.derive(load())["concepts"]}
        self.assertEqual(labels["retry-ledger"], "Documented source (supplied evidence)")
        self.assertEqual(labels["parallel-review"], lineage.ORIGIN_LABEL_UNRESOLVED)

    def test_empty_source_only_and_zero_consumer_graphs(self):
        empty = {"schema_version": "concept-lineage/1", "data_class": "public", "sources": [], "concepts": [],
                 "consumers": [], "uses": [], "evidence": [], "refinements": []}
        self.assertIsNone(code(empty))
        proj = lineage.build_projection(empty, "0" * 64)
        self.assertIn("No concepts recorded.", lineage.render_html(proj))
        env = load()
        for key in ("concepts", "consumers", "uses", "evidence", "refinements"):
            env[key] = []
        self.assertIsNone(code(env))
        env = load()
        env["uses"], env["evidence"], env["refinements"] = [], [], []
        for concept in env["concepts"]:
            if concept["relationship"] == "documented_origin":
                concept["relationship"], concept["origin_evidence_id"] = "conceptual_similarity", None
        self.assertIsNone(code(env))

    def test_eighty_advisory_concepts_stay_proposals(self):
        env = {"schema_version": "concept-lineage/1", "data_class": "synthetic_public", "sources": [],
               "concepts": [], "consumers": [], "uses": [], "evidence": [], "refinements": []}
        for n in range(80):
            sid = "%sadvisory:adv-%03d" % (P, n)
            env["sources"].append({
                "id": sid, "owner": "example/lineage-demo", "record_kind": "advisory", "record_id": "adv-%03d" % n,
                "title": "Advisory %d" % n, "url": "https://arxiv.org/abs/0000.%05d" % n,
                "upstream_version": {"kind": "unknown", "value": None, "reason": "not_captured"},
                "catalog_revision": git("c"), "aliases": [], "evidence_depth": "unverified"})
            env["concepts"].append({
                "id": "%sconcept:adv-%03d" % (P, n), "owner": "example/lineage-demo", "title": "Proposal %d" % n,
                "summary": "Advisory proposal, not adopted.", "source_ids": [sid],
                "relationship": "conceptual_similarity", "origin_evidence_id": None})
        view = lineage.derive(env)
        self.assertEqual(sum(view["totals"].values()), 0)
        self.assertEqual(len(view["concepts"]), 80)


class IdentityTests(unittest.TestCase):
    def test_bad_ids(self):
        bad = [A + "\n", "alpha", P + "repository:", P + "repository:a/../b", P + "repository:a//b",
               P + "repository:a/.", P + "bogus:alpha", "x" * 200 + ":repository:a", P + "repository:\u00e9"]
        for ident in bad:
            env = load()
            env["sources"][0]["id"] = ident
            self.assertEqual(code(env), "bad_id", ident)

    def test_kind_agreement_and_case_conflict(self):
        env = load()
        env["sources"][0]["record_kind"] = "research"
        self.assertEqual(code(env), "source_kind")
        env = load()
        env["sources"][2]["id"] = A.upper().replace("REPOSITORY", "repository").replace("EXAMPLE/LINEAGE-DEMO", "example/lineage-demo")
        env["sources"][2]["id"] = P + "repository:ALPHA"
        env["sources"][2]["record_id"] = "ALPHA"
        self.assertEqual(code(env), "duplicate_id")

    def test_cross_array_duplicate_id(self):
        env = load()
        env["consumers"][0]["id"] = "example/consumer-one:consumer:one"
        env["consumers"][1]["id"] = env["consumers"][0]["id"]
        env["consumers"][1]["owner"] = env["consumers"][0]["owner"]
        self.assertEqual(code(env), "duplicate_id")

    def test_aliases(self):
        env = load()
        env["sources"][0]["aliases"] = [env["sources"][2]["id"]]
        self.assertEqual(code(env), "alias_conflict")
        env = load()
        env["sources"][0]["aliases"] = [P + "repository:alias-a"]
        env["sources"][2]["aliases"] = [P + "repository:alias-a"]
        self.assertEqual(code(env), "alias_conflict")
        env = load()
        env["sources"][0]["aliases"] = [A]
        self.assertEqual(code(env), "alias_conflict")
        env = load()
        env["sources"][0]["aliases"] = [P + "repository:alias-a"]
        env["sources"][2]["aliases"] = [P + "repository:ALIAS-A"]
        self.assertEqual(code(env), "alias_conflict")

    def test_unknown_and_missing_fields(self):
        env = load()
        env["sources"][0]["extra"] = "x"
        self.assertEqual(code(env), "unknown_field")
        env = load()
        del env["uses"][0]["refinement"]
        self.assertEqual(code(env), "missing_field")
        env = load()
        env["extra"] = []
        self.assertEqual(code(env), "unknown_field")

    def test_text_rules(self):
        for bad in ("e\u0301", "a\u202eb", "a\u200bb", "line\nbreak", "a\u2028b", "C:\\Users\\x\\file", "/home/user/x"):
            env = load()
            env["sources"][0]["title"] = bad
            self.assertIsNotNone(code(env), repr(bad))
        env = load()
        env["sources"][0]["title"] = "x" * 2049
        self.assertEqual(code(env), "too_long")


class UrlTests(unittest.TestCase):
    def test_urls(self):
        base = "https://github.com/example-org/alpha-tool"
        bad = ["http://github.com/a/b", "https://GitHub.com/a/b", "https://github.com./a/b", "https://gıthub.com/a/b",
               "https://xn--github-9d2a.com/a/b", "https://user@github.com/a/b", "https://github.com:443/a/b",
               base + "?x=1", base + "#f", base + " x", base + "\\x", base + "/%2e%2e/x", base + "/%2E/x",
               base + "/%252e%252e/x", base + "/../x", base + "//x", "https://example.com/a/b", "https://github.com",
               base + "\t", "https://github.com/a/b\n"]
        for url in bad:
            env = load()
            env["sources"][0]["url"] = url
            self.assertEqual(code(env), "bad_url", url)
        env = load()
        env["sources"][2]["url"] = "https://arxiv.org/abs/1234.5678"
        self.assertIsNone(code(env))


class OriginTests(unittest.TestCase):
    def test_valid_origin_has_no_consumer_or_use(self):
        env = load()
        origin = row(env, "evidence", P + "evidence:origin-retry")
        self.assertNotIn("use_id", origin)
        self.assertNotIn("consumer_id", origin)
        self.assertIsNone(code(env))

    def test_wrong_repository_and_revision(self):
        env = load()
        row(env, "evidence", P + "evidence:origin-retry")["url"] = "https://github.com/other/alpha-tool/commit/" + "3" * 40
        self.assertEqual(code(env), "origin_url_mismatch")
        env = load()
        row(env, "evidence", P + "evidence:origin-retry")["source_revision"] = git("4")
        self.assertEqual(code(env), "origin_url_mismatch")

    def test_consumer_repository_url_rejected(self):
        env = load()
        row(env, "evidence", P + "evidence:origin-retry")["url"] = "https://github.com/example/consumer-one/commit/" + "3" * 40
        self.assertEqual(code(env), "origin_url_mismatch")

    def test_publication_origin(self):
        env = load()
        row(env, "evidence", P + "evidence:origin-citation")["source_revision"] = {"kind": "publication", "value": "v3", "reason": None}
        self.assertEqual(code(env), "origin_url_mismatch")
        env = load()
        row(env, "evidence", P + "evidence:origin-citation")["url"] = "https://doi.org/10.0000/other"
        self.assertEqual(code(env), "origin_url_mismatch")

    def test_unknown_or_missing_digest_cannot_document(self):
        env = load()
        o = row(env, "evidence", P + "evidence:origin-retry")
        o["artifact_sha256"], o["missing_reason"] = None, "receipt_absent"
        self.assertEqual(code(env), "origin_incomplete")
        env = load()
        o = row(env, "evidence", P + "evidence:origin-retry")
        o["result"] = "unknown"
        self.assertEqual(code(env), "origin_incomplete")
        env = load()
        o = row(env, "evidence", P + "evidence:origin-retry")
        o["source_revision"] = {"kind": "unknown", "value": None, "reason": "not_captured"}
        o["url"], o["missing_reason"] = None, "not_captured"
        self.assertEqual(code(env), "origin_incomplete")

    def test_origin_on_another_concept(self):
        env = load()
        row(env, "concepts", P + "concept:handoff-notes").update({"relationship": "documented_origin", "origin_evidence_id": P + "evidence:origin-retry"})
        self.assertEqual(code(env), "origin_unreferenced")

    def test_origin_row_must_be_referenced_and_other_relationships_null(self):
        env = load()
        row(env, "concepts", RETRY)["origin_evidence_id"] = None
        self.assertEqual(code(env), "origin_missing")
        env = load()
        row(env, "concepts", RETRY)["relationship"] = "appraised_mechanism"
        self.assertEqual(code(env), "origin_not_allowed")
        env = load()
        row(env, "concepts", P + "concept:parallel-review")["origin_evidence_id"] = P + "evidence:origin-retry"
        self.assertEqual(code(env), "origin_not_allowed")

    def test_origin_through_use_rejected(self):
        env = load()
        row(env, "uses", P + "use:retry-four")["evidence_ids"].append(P + "evidence:origin-retry")
        self.assertEqual(code(env), "evidence_binding")

    def test_origin_source_must_belong_to_concept(self):
        env = load()
        row(env, "evidence", P + "evidence:origin-retry")["source_id"] = P + "repository:beta"
        self.assertEqual(code(env), "origin_source_mismatch")


class BindingTests(unittest.TestCase):
    def test_duplicate_concept_consumer_use(self):
        env = load()
        dup = copy.deepcopy(row(env, "uses", P + "use:retry-four"))
        dup["id"] = P + "use:retry-four-b"
        env["uses"].append(dup)
        self.assertEqual(code(env), "duplicate_use")

    def test_unlisted_orphan_and_cross_use_evidence(self):
        env = load()
        row(env, "uses", P + "use:retry-one")["evidence_ids"].remove(P + "evidence:c2")
        self.assertEqual(code(env), "evidence_binding")
        env = load()
        row(env, "evidence", P + "evidence:c2")["use_id"] = P + "use:missing"
        self.assertEqual(code(env), "orphan_evidence")
        env = load()
        row(env, "uses", P + "use:retry-two")["evidence_ids"].append(P + "evidence:c2")
        self.assertEqual(code(env), "evidence_binding")
        env = load()
        row(env, "uses", P + "use:retry-one")["evidence_ids"].append(P + "evidence:c2")
        self.assertEqual(code(env), "duplicate_evidence_id")

    def test_wrong_consumer_and_url(self):
        env = load()
        row(env, "evidence", P + "evidence:c1")["consumer_id"] = "example/consumer-two:consumer:two"
        self.assertEqual(code(env), "evidence_consumer_mismatch")
        env = load()
        row(env, "evidence", P + "evidence:c1")["url"] = "https://github.com/example/consumer-two/commit/" + "4" * 40
        self.assertEqual(code(env), "url_mismatch")
        env = load()
        row(env, "evidence", P + "evidence:c1")["url"] = "https://github.com/example/consumer-one/commit/" + "5" * 40
        self.assertEqual(code(env), "url_mismatch")
        env = load()
        row(env, "evidence", P + "evidence:c1")["consumer_revision"] = {"kind": "publication", "value": "v1", "reason": None}
        self.assertEqual(code(env), "url_mismatch")

    def test_forged_digest_and_reason_rules(self):
        env = load()
        row(env, "evidence", P + "evidence:c1")["artifact_sha256"] = "AB" * 32
        self.assertEqual(code(env), "bad_digest")
        env = load()
        row(env, "evidence", P + "evidence:c1")["artifact_sha256"] = None
        self.assertEqual(code(env), "missing_reason")
        env = load()
        row(env, "evidence", P + "evidence:c1")["missing_reason"] = "receipt_absent"
        self.assertEqual(code(env), "missing_reason")

    def test_results_by_kind(self):
        env = load()
        row(env, "evidence", P + "evidence:c1")["result"] = "pass"
        self.assertEqual(code(env), "bad_enum")
        env = load()
        row(env, "evidence", P + "evidence:t1")["result"] = "observed"
        self.assertEqual(code(env), "bad_enum")

    def test_timestamps(self):
        for bad in ("2026-01-02T03:04:05", "2026-13-02T03:04:05Z", "2026-01-02 03:04:05Z", "2026-01-02T03:04:05+24:00"):
            env = load()
            row(env, "evidence", P + "evidence:c1")["observed_at"] = bad
            self.assertEqual(code(env), "bad_timestamp", bad)
        env = load()
        row(env, "evidence", P + "evidence:c1")["observed_at"] = "2026-01-02T03:04:05.123+01:00"
        self.assertIsNone(code(env))

    def test_source_versions_map_must_match_concept_sources(self):
        env = load()
        row(env, "uses", P + "use:retry-four")["source_versions_used"] = {}
        self.assertEqual(code(env), "source_versions_mismatch")

    def test_versions_strict(self):
        env = load()
        env["sources"][0]["upstream_version"] = {"kind": "git", "value": "ABC", "reason": None}
        self.assertEqual(code(env), "bad_version")
        env = load()
        env["sources"][0]["upstream_version"] = {"kind": "unknown", "value": None, "reason": "nope"}
        self.assertEqual(code(env), "bad_enum")
        env = load()
        env["sources"][0]["upstream_version"] = {"kind": "git", "value": "a" * 40}
        self.assertEqual(code(env), "missing_field")


class RefinementTests(unittest.TestCase):
    def test_cycle_self_and_unrelated_evidence(self):
        env = load()
        env["refinements"].append({"id": P + "refinement:back", "from_concept_id": P + "concept:handoff-notes",
                                   "to_concept_id": RETRY, "summary": "loop", "evidence_ids": []})
        self.assertEqual(code(env), "derivation_cycle")
        env = load()
        env["refinements"][0]["to_concept_id"] = RETRY
        self.assertEqual(code(env), "self_refinement")
        env = load()
        env["refinements"][0]["evidence_ids"] = [P + "evidence:origin-citation"]
        self.assertEqual(code(env), "unrelated_evidence")
        env = load()
        env["refinements"][0]["evidence_ids"] = [P + "evidence:c1"]
        self.assertIsNone(code(env))


class PrivacyAndProjectionTests(unittest.TestCase):
    def test_private_consumer_and_class(self):
        env = load()
        env["consumers"][0]["visibility"] = "private"
        self.assertEqual(code(env), "private_in_public")
        env["data_class"] = "private_metadata"
        self.assertEqual(code(env), "bad_enum")
        self.assertIsNone(code(env, allow_private=True))

    def test_projection_checks(self):
        proj = lineage.build_projection(load(), "1" * 64)
        lineage.validate_projection(proj)
        bad = copy.deepcopy(proj)
        bad["packet_sha256"] = "0" * 64
        with self.assertRaises(lineage.LineageError):
            lineage.validate_projection(bad)
        bad = copy.deepcopy(proj)
        bad["authority_granted"] = True
        with self.assertRaises(lineage.LineageError):
            lineage.validate_projection(bad)
        bad = copy.deepcopy(proj)
        bad["extra"] = 1
        with self.assertRaises(lineage.LineageError):
            lineage.validate_projection(bad)
        self.assertFalse(proj["independent_authenticity_verified"])


class RenderTests(unittest.TestCase):
    def render(self, env):
        return lineage.render_html(lineage.build_projection(env, "2" * 64))

    def test_committed_demo_is_regenerated_output(self):
        data = (HERE / "fixture.json").read_bytes()
        expected = lineage.render_html(lineage.build_projection(json.loads(data), lineage.sha256_hex(data)))
        self.assertEqual((HERE / "lineage.html").read_bytes(), expected.encode("utf-8"))

    def test_csp_hashes_match_inline_content(self):
        page = self.render(load())
        csp = re.search(r'http-equiv="Content-Security-Policy" content="([^"]+)"', page).group(1)
        for needle in ("default-src 'none'", "connect-src 'none'", "base-uri 'none'", "form-action 'none'"):
            self.assertIn(needle.replace("'", "&#x27;"), csp)
        self.assertNotIn("unsafe-inline", csp)
        self.assertNotIn("nonce", page)
        style = re.search(r"<style>(.*?)</style>", page, re.S).group(1)
        script = re.search(r"<script>(.*?)</script>", page, re.S).group(1)
        for body in (style, script):
            digest = base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
            self.assertIn("sha256-" + digest, csp)
        self.assertEqual(page.count("<script>"), 1)

    def test_hostile_text_is_escaped(self):
        env = load()
        env["sources"][0]["title"] = '</script><img src=x onerror=alert(1)> <!-- & "q"'
        page = self.render(env)
        self.assertNotIn("<img", page)
        self.assertNotIn("<!-- &", page)
        data = re.search(r'id="lineage-data">(.*?)</script>', page, re.S).group(1)
        self.assertNotIn("<", data)
        self.assertNotIn("\u2028", page)
        self.assertEqual(json.loads(data)["sources"][0]["title"], env["sources"][0]["title"])

    def test_links_and_no_external_loads(self):
        page = self.render(load())
        self.assertNotIn("src=\"http", page)
        self.assertNotIn("<link", page)
        self.assertNotIn("fetch(", page)
        for tag in re.findall(r"<a [^>]*>", page):
            self.assertIn('rel="noopener noreferrer"', tag)
        self.assertIn("Documented source (supplied evidence)", page)
        self.assertIn(lineage.ORIGIN_LABEL_UNRESOLVED, page)
        self.assertIn("prefers-reduced-motion", page)
        self.assertIn("focus-visible", page)

    def test_table_graph_parity_data(self):
        page = self.render(load())
        view = json.loads(re.search(r'id="lineage-data">(.*?)</script>', page, re.S).group(1))
        rows = len(re.findall(r"<tr><td>", re.search(r'id="use-table".*?</table>', page, re.S).group(0)))
        self.assertEqual(rows, sum(max(1, len(c["uses"])) for c in view["concepts"]))


class ContractTests(unittest.TestCase):
    def test_contract_matches_engine(self):
        contract = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["schema_version"], lineage.SCHEMA)
        self.assertEqual(contract["id_pattern"], lineage.ID_PATTERN)
        self.assertEqual(contract["limits"], dict(lineage.LIMITS, input_bytes=lineage.MAX_INPUT, depth=lineage.MAX_DEPTH,
                                                  string_chars=lineage.MAX_STRING, identifier_chars=lineage.MAX_ID,
                                                  html_bytes=lineage.MAX_HTML))
        rows = contract["rows"]
        self.assertEqual(set(rows["source"]), lineage.SOURCE_KEYS)
        self.assertEqual(set(rows["concept"]), lineage.CONCEPT_KEYS)
        self.assertEqual(set(rows["consumer"]), lineage.CONSUMER_KEYS)
        self.assertEqual(set(rows["use"]), lineage.USE_KEYS)
        self.assertEqual(set(rows["use_evidence"]), lineage.USE_EVIDENCE_KEYS)
        self.assertEqual(set(rows["origin_evidence"]), lineage.ORIGIN_EVIDENCE_KEYS)
        self.assertEqual(set(rows["refinement"]), lineage.REFINEMENT_KEYS)
        self.assertEqual(set(contract["envelope"]), lineage.ENVELOPE_KEYS)
        self.assertEqual(set(contract["projection"]), lineage.PROJECTION_KEYS)
        self.assertEqual(tuple(contract["enums"]["relationship"]), lineage.RELATIONSHIPS)
        self.assertEqual(tuple(contract["enums"]["decision"]), lineage.DECISIONS)
        self.assertEqual(tuple(contract["approved_hosts"]), lineage.APPROVED_HOSTS)
        self.assertEqual(tuple(contract["buckets"]), lineage.BUCKETS)
        envelopes = contract["envelopes"]
        self.assertEqual(envelopes["mapping"]["schema_version"], lineage.MAPPING_SCHEMA)
        self.assertEqual(set(envelopes["mapping"]), lineage.MAPPING_DOC_KEYS)
        self.assertEqual(set(envelopes["mapping"]["mappings"]), set(lineage.MAPPING_ARRAYS))
        self.assertEqual(envelopes["admission"]["schema_version"], lineage.ADMISSION_SCHEMA)
        self.assertEqual(set(envelopes["admission"]), lineage.ADMISSION_KEYS)
        self.assertEqual(envelopes["input_manifest"]["schema_version"], lineage.INPUT_SCHEMA)
        self.assertEqual(set(envelopes["input_manifest"]), lineage.INPUT_MANIFEST_KEYS)
        self.assertEqual(set(envelopes["input_item"]), lineage.INPUT_ITEM_KEYS)
        self.assertEqual(envelopes["pin"]["schema_version"], lineage.PIN_SCHEMA)
        self.assertEqual(set(envelopes["pin"]), lineage.PIN_KEYS)
        self.assertIn("tagged", rows["source"]["catalog_revision"])


class CorrectionRegressionTests(unittest.TestCase):
    def test_catalog_revision_is_tagged_version(self):
        env = load()
        env["sources"][0]["catalog_revision"] = "c" * 40
        self.assertEqual(code(env), "type")
        env["sources"][0]["catalog_revision"] = {"kind": "git", "value": "C" * 40, "reason": None}
        self.assertEqual(code(env), "bad_version")

    def test_unhashable_source_id_members_fail_content_free(self):
        for member in ({}, [], None, 7):
            env = load()
            env["concepts"][0]["source_ids"] = [member]
            self.assertEqual(code(env), "bad_id")

    def test_duplicate_refinement_edge(self):
        env = load()
        extra = copy.deepcopy(env["refinements"][0])
        extra["id"] = P + "refinement:duplicate-edge"
        env["refinements"].append(extra)
        self.assertEqual(code(env), "duplicate_refinement_edge")

    def test_owner_and_record_id_bind_to_qualified_id(self):
        for key, field, value, expected in (
                ("sources", "owner", "example/other", "owner_mismatch"),
                ("sources", "record_id", "other", "record_id_mismatch"),
                ("concepts", "owner", "example-org", "owner_mismatch"),
                ("consumers", "owner", "example", "owner_mismatch")):
            env = load()
            env[key][0][field] = value
            self.assertEqual(code(env), expected)

    def envelope_code(self, func, *args):
        try:
            func(*args)
        except lineage.LineageError as exc:
            return exc.code
        return None

    def mapping_doc(self):
        mappings = {name: [] for name in lineage.MAPPING_ARRAYS}
        return {"schema_version": lineage.MAPPING_SCHEMA, "mappings": mappings, "admission": {
            "schema_version": lineage.ADMISSION_SCHEMA, "packet_sha256": lineage.canonical_sha256(mappings),
            "policy_sha256": "a" * 64, "classification": "public",
            "review_record_ref": "example/catalog:evidence:review-1"}}

    def test_mapping_document_exact(self):
        check = lambda doc: self.envelope_code(lineage.validate_mapping_document, doc, "a" * 64)
        self.assertIsNone(check(self.mapping_doc()))
        doc = self.mapping_doc(); doc["extra"] = 1
        self.assertEqual(check(doc), "unknown_field")
        doc = self.mapping_doc(); doc["admission"]["schema_version"] = "concept-lineage-admission/2"
        self.assertEqual(check(doc), "schema_version")
        doc = self.mapping_doc(); doc["admission"]["policy_sha256"] = "b" * 64
        self.assertEqual(check(doc), "policy_digest")
        doc = self.mapping_doc(); doc["mappings"]["concepts"] = {}
        self.assertEqual(check(doc), "type")
        for ref in ("example/catalog:evidence:a/../b", "example/catalog:evidence:./a", "example/catalog::x", 5):
            doc = self.mapping_doc(); doc["admission"]["review_record_ref"] = ref
            self.assertEqual(check(doc), "bad_id")

    def manifest(self):
        return {"schema_version": lineage.INPUT_SCHEMA, "catalog_revision": git("a"), "builder_revision": git("b"),
                "supplier_revision": git("c"), "contract_sha256": "1" * 64, "runtime_sha256": "2" * 64,
                "builder_sha256": "3" * 64, "mapping_sha256": "4" * 64,
                "inputs": [{"path": "docs/a.json", "sha256": "5" * 64, "revision": git("b")}]}

    def test_input_manifest_exact(self):
        check = lambda doc: self.envelope_code(lineage.validate_input_manifest, doc)
        self.assertIsNone(check(self.manifest()))
        for field, value, expected in (("catalog_revision", "a" * 40, "type"),
                                       ("builder_revision", {"kind": "unknown", "value": None, "reason": "not_captured"}, "bad_version"),
                                       ("supplier_revision", "c" * 40, "type"), ("mapping_sha256", None, "bad_digest"),
                                       ("schema_version", "concept-lineage-input/2", "schema_version")):
            doc = self.manifest(); doc[field] = value
            self.assertEqual(check(doc), expected)
        doc = self.manifest(); doc["inputs"][0]["path"] = "../secret"
        self.assertEqual(check(doc), "bad_path")
        doc = self.manifest(); doc["inputs"][0]["extra"] = True
        self.assertEqual(check(doc), "unknown_field")

    def test_pin_chain(self):
        packet = load()
        manifest_bytes = lineage.canonical_bytes(self.manifest())
        projection_bytes = lineage.canonical_bytes(lineage.build_projection(packet, lineage.sha256_hex(manifest_bytes)))
        pin = {"schema_version": lineage.PIN_SCHEMA, "owner_repository": "example/catalog"}
        for name in ("catalog_revision", "builder_revision", "supplier_revision", "contract_sha256",
                     "runtime_sha256", "builder_sha256", "mapping_sha256"):
            pin[name] = self.manifest()[name]
        pin.update(projection_revision=git("d"), input_manifest_sha256=lineage.sha256_hex(manifest_bytes),
                   projection_sha256=lineage.sha256_hex(projection_bytes))
        check = lambda doc, m=manifest_bytes, p=projection_bytes: self.envelope_code(lineage.verify_pin_chain, doc, m, p)
        self.assertIsNone(check(pin))
        self.assertEqual(check(dict(pin, supplier_revision="c" * 40)), "type")
        self.assertEqual(check(dict(pin, latest=True)), "unknown_field")
        self.assertEqual(check(dict(pin, mapping_sha256="9" * 64)), "pin_mismatch")
        self.assertEqual(check(dict(pin, projection_sha256="9" * 64)), "projection_digest")
        self.assertEqual(check(pin, manifest_bytes + b" "), "not_canonical")


class CliTests(unittest.TestCase):
    def test_unhashable_member_exits_two_without_traceback(self):
        env = load()
        env["concepts"][0]["source_ids"] = [{}]
        path = HERE / "_probe_unhashable.json"
        try:
            path.write_text(json.dumps(env), encoding="utf-8")
            result = self.run_cli("validate", path.name)
        finally:
            path.unlink()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr.strip(), b"invalid: bad_id")
        self.assertNotIn(b"Traceback", result.stderr)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-I", str(HERE / "lineage.py")] + list(args),
                              capture_output=True, cwd=str(HERE))

    def test_validate_and_failure_without_traceback(self):
        ok = self.run_cli("validate", "fixture.json")
        self.assertEqual(ok.returncode, 0)
        self.assertIn(b"valid sources=3", ok.stdout)
        bad = self.run_cli("validate", "contract.json")
        self.assertEqual(bad.returncode, 2)
        self.assertNotIn(b"Traceback", bad.stderr)
        self.assertEqual(self.run_cli("validate", "missing.json").returncode, 2)

    def test_project_is_byte_deterministic(self):
        first = self.run_cli("project", "fixture.json")
        second = self.run_cli("project", "fixture.json")
        self.assertEqual(first.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)
        self.assertTrue(first.stdout.endswith(b"}\n"))
        self.assertNotIn(b"\r", first.stdout)


if __name__ == "__main__":
    unittest.main()
