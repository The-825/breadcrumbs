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

Envelope keys are exactly `schema_version` (`concept-lineage/1`), `data_class`, `sources`, `concepts`, `consumers`, `uses`, `evidence`, `refinements`. Unknown or missing fields, duplicate JSON keys, a BOM, invalid UTF-8, non-finite or oversized numbers and nesting deeper than 12 fail with a content-free code. Input is capped at 2 MiB, strings at 2048 characters, identifiers at 180. `contract.json` lists every row key, enum and limit.

- IDs are `owner/name:kind:local` (ASCII, matched with `fullmatch`, case-insensitively unique). Owner-qualified `research:001` and `repository:R-001` are distinct. Aliases come only from the owning source record, are one hop, and may not collide with any ID or alias.
- A version is always `{kind, value, reason}`: `git` (40 lowercase hex), `publication` (bounded string) or `unknown` (null value with a reason code). Upstream version, catalog revision, consumer commit, contract version and byte digest are never interchanged.
- URLs are HTTPS on exactly `github.com`, `doi.org` or `arxiv.org`, with no userinfo, port, query, fragment, backslash, whitespace or decoded dot segments. A safe URL shape is not privacy approval or proof of identity.
- Public paths accept `public` and `synthetic_public` data and reject private consumers. A private adapter in an owning runtime may opt in to `private_metadata`.

## Origin versus consumer evidence

A concept with relationship `documented_origin` points at one origin row (`kind: origin`). That row has no use or consumer fields. It must be observed, carry a digest and a known source revision, and its URL must be the source repository's commit URL at that revision (Git) or equal the source's publication URL with a matching publication version. Origin rows nobody references, rows attached to another concept, and origin rows listed in a use's `evidence_ids` are rejected. The label is `Documented source (supplied evidence)`: a supplied attribution, not authenticated code borrowing or consumer adoption. A similarity record with no origin shows `Origin unresolved; not borrowed`.

## Use evidence rules

One use per (concept, consumer). Its `evidence_ids` must equal the complete set of non-origin evidence rows naming that use, and each such row must name the same consumer. A change counts only when observed, with a known Git revision and a digest. A synthetic test pairs with a change only when it passes, has a digest and shares the change's exact revision; otherwise it shows `unmatched test revision` or `reported pass, receipt absent`. Mixed pass and fail receipts stay visible. Merge, deployment and runtime receipts show `revision match only` when equal to a supplied change revision, else `relation to change revision unverified`. A commit URL on use evidence must be the consumer repository (the owner/name prefix of the consumer ID) at that revision.

Per concept, consumers are counted in exactly one bucket each: proposed; accepted without observed change; accepted with observed change; rejected; deferred. Freshness compares a recorded source version with the current one: `revision_match`, `revision_changed_scope_unknown` or `unverified`. Revision inequality never asserts material change or quality, and there is no blended score.

## Projection and page

`project` wraps a validated packet as `concept-lineage-projection/1` with the packet's canonical SHA-256 (sorted keys, UTF-8, trailing LF, no timestamp) and the flags `independent_authenticity_verified` and `authority_granted`, both false. `render` accepts only a validated projection and writes one page with a hash-based Content-Security-Policy (`default-src 'none'`, no `unsafe-inline`, no nonce, `connect-src 'none'`), a list view, a graph view with the same rows, keyboard-focusable scrolling tables and an empty state. The graph script renders data only and is not a second validator. Browser behavior is not covered by the unit tests.
