# Workflow source contract 1.1

This contract extends the public Breadcrumbs workflow registry to primary
documentation and research sources. The Python 3 validator ships in
`scripts/workflow_registry.py`; it uses only the standard library. This is a
descriptive discovery contract. It does not authorize downloads, installation,
execution, persistent private data, consumer changes or publication.

## Select the version explicitly

Registry version `1.0` retains its Reddit-only source contract. Version `1.1`
accepts `community-post`, `repository-documentation`, `official-documentation`
and `research-publication`. Routing remains version `1.0` and keeps its existing
completion contracts. Existing community records can migrate without inventing
historical source pins. New primary documentation or research records require
the pin below. Every source URL uses HTTPS without embedded credentials.

## Pin a primary source

Add a `source_pin` object with these fields:

| Field | Required evidence |
|---|---|
| `canonical_url` | Exactly the record's `source_url`, after identity and alias review. |
| `version` | Reviewed repository commit, publication version or dated document edition. |
| `retrieved_date` | Actual retrieval date in `YYYY-MM-DD` format. |
| `content_sha256` | Lowercase SHA-256 of the retrieved source bytes. |
| `license_status` | Observed license or explicit `unknown`; this is not code-use permission. |

The validator checks record consistency. It does not fetch the source or verify
the collector's testimony. A reviewer checks the retrieval receipt, canonical
identity, version, licensing, overlap and claim boundaries. Keep inaccessible
sources as unverified leads instead of inventing pins. Do not copy source text or
code without its attribution and licensing duties.

## Move a record through review

1. Retain a discovery lead with its concrete problem, source, uncertainty and next
   check. Compare existing workflows before assigning a stable workflow ID.
2. Screen the primary description and record requirements, usable steps,
   limitations and validation signals. A screened article remains unproven for
   workplace effectiveness.
3. Claim `reproduced` only with a passing bounded check, its command, recorded
   date and claim boundary. The registry stores the receipt; a real test run is
   separate evidence. The reproduction runner executes only its reviewed local
   command allowlist, never arbitrary commands from a submitted record.
4. Claim `adopted` only with an owner, completion test, result evidence URL and
   correction path in an `adoption` object. Adoption in a consuming system remains
   that system's decision. Keep private result evidence in its owning runtime.

Practical article fields live in `guide`: when to use or skip it, requirements,
steps, a synthetic example, a completion check, failure modes and attributed
artifact links. Discovery records without a guide do not become site articles.
All records retain `authority: descriptive-only`.

Validate and render with `python scripts/workflow_registry.py --check` and
`python scripts/workflow_registry.py --write`. The former never ingests a source;
the latter renders the existing registry view. Neither command searches the web,
adds a workflow or grants consumer authority.
