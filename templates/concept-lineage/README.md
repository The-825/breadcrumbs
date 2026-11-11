# Concept lineage (read-only)

A portable, standard-library Python 3.9+ validator and renderer for one JSON graph that links public source records to concepts and to the consumers that used them. It never executes source code, opens a network connection, reads a clock or writes outside the path you name. Every label describes supplied evidence, not independent authenticity, release authority or adoption.

Files: `contract.json` (fixed shapes and limits), `lineage.py` (validator, projection, renderer, CLI), `fixture.json` (fictional graph), `lineage.html` (the demo generated from the fixture), `test_lineage.py`.

```
python3 templates/concept-lineage/lineage.py validate templates/concept-lineage/fixture.json
python3 templates/concept-lineage/lineage.py project templates/concept-lineage/fixture.json > projection.json
python3 templates/concept-lineage/lineage.py render projection.json -o lineage.html
python3 -m unittest discover -s templates/concept-lineage
```

## Graph shape

Packet normalization sorts records by ID and sorts alias, source-reference and evidence-reference sets. Equivalent permutations produce the same packet digest, projection and rendered page. Narrative text and version values keep their meaning and order. Validation runs before normalization, so duplicate or malformed input is rejected rather than repaired.

Envelope keys are exactly `schema_version` (`concept-lineage/1`), `data_class`, `sources`, `concepts`, `consumers`, `uses`, `evidence`, `refinements`. Unknown or missing fields, duplicate JSON keys, a BOM, invalid UTF-8, non-finite or oversized numbers and nesting deeper than 12 fail with a content-free code. Input is capped at 2 MiB, strings at 2048 characters, identifiers at 180. `contract.json` lists every row key, enum and limit.

- IDs are `owner/name:kind:local` (ASCII, matched with `fullmatch`, case-insensitively unique). Owner-qualified `research:001` and `repository:R-001` are distinct. Aliases come only from the owning source record, are one hop, and may not collide with any ID or alias.
- Each source, concept and consumer `owner` equals its ID's `owner/name` prefix, and a source `record_id` equals the ID's local part. This keeps provenance consistent; it does not authenticate ownership.
- A version is always `{kind, value, reason}`: `git` (40 lowercase hex), `publication` (bounded string) or `unknown` (null value with a reason code). Source `upstream_version` and `catalog_revision` are both tagged versions. Upstream version, catalog revision, consumer commit, contract version and byte digest are never interchanged.
- Refinements join two different concepts, at most once per (from, to) pair, without cycles.
- URLs are HTTPS on exactly `github.com`, `doi.org` or `arxiv.org`, with no userinfo, port, query, fragment, backslash, whitespace or decoded dot segments. A safe URL shape is not privacy approval or proof of identity.
- Public paths accept `public` and `synthetic_public` data and reject private consumers. A private adapter in an owning runtime may opt in to `private_metadata`.

## Origin versus consumer evidence

A concept with relationship `documented_origin` points at one origin row (`kind: origin`). That row has no use or consumer fields. It must be observed, carry a digest and a known source revision, and its URL must be the source repository's commit URL at that revision (Git) or equal the source's publication URL with a matching publication version. Origin rows nobody references, rows attached to another concept, and origin rows listed in a use's `evidence_ids` are rejected. The label is `Documented source (supplied evidence)`: a supplied attribution, not authenticated code borrowing or consumer adoption. A similarity record with no origin shows `Origin unresolved; not borrowed`.

## Use evidence rules

One use per (concept, consumer). Its `evidence_ids` must equal the complete set of non-origin evidence rows naming that use, and each such row must name the same consumer. A change counts only when observed, with a known Git revision and a digest. A synthetic test pairs with a change only when it passes, has a digest and shares the change's exact revision; otherwise it shows `unmatched test revision` or `reported pass, receipt absent`. Mixed pass and fail receipts stay visible. Merge, deployment and runtime receipts show `revision match only` when equal to a supplied change revision, else `relation to change revision unverified`. A commit URL on use evidence must be the consumer repository (the owner/name prefix of the consumer ID) at that revision.

Per concept, consumers are counted in exactly one bucket each: proposed; accepted without observed change; accepted with observed change; rejected; deferred. Freshness compares a recorded source version with the current one: `revision_match`, `revision_changed_scope_unknown` or `unverified`. Revision inequality never asserts material change or quality, and there is no blended score.

## Projection and page

`project` wraps a validated packet as `concept-lineage-projection/1` with the packet's canonical SHA-256 (sorted keys, UTF-8, trailing LF, no timestamp) and the flags `independent_authenticity_verified` and `authority_granted`, both false. A projection whose packet is not in normalized order fails with `not_normalized`, so one graph has one packet digest. `render` accepts only a validated projection and writes one page with a hash-based Content-Security-Policy (`default-src 'none'`, no `unsafe-inline`, no nonce, `connect-src 'none'`), a table view and a graph view, keyboard-focusable scrolling tables and an empty state. The graph view lays out each concept as sources → concept → consumers and carries the same evidence as the table: origin and derivation, adaptation and refinement narrative, observed changes, matched and unmatched test receipts, release relations and source freshness. One filter applies to both views. The graph script renders data only with text nodes and is not a second validator. Browser behavior is not covered by the unit tests.

## Supplier envelopes

A consumer that builds or pins a projection uses the same pure helpers: `validate_mapping_document` (`concept-lineage-mappings/1` wrapper with exact `concepts`/`consumers`/`uses`/`evidence`/`refinements` arrays and a `concept-lineage-admission/1` record binding the canonical mappings digest, the contract digest, a public classification and a full-grammar review record reference), `validate_input_manifest` (`concept-lineage-input/1`), `validate_pin` (`concept-lineage-pin/1`) and `verify_pin_chain`, which checks a pin against exact canonical manifest and projection bytes. Every persisted revision in these envelopes is a tagged Git version; unknown keys, other schema versions and string revisions fail. Shape and digest consistency do not authenticate a reviewer or publisher.
