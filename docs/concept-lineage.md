# Concept lineage

Concept lineage answers three reader questions from supplied records: where did an idea come from, which consumers decided what about it, and what receipts back those decisions. It is a read-only view. It adds no datastore, collects nothing, calls no network and grants no authority.

The portable kit lives in [templates/concept-lineage](../templates/concept-lineage/README.md): a fixed [contract](../templates/concept-lineage/contract.json), a Python 3.9+ standard-library validator and renderer, a fictional [fixture](../templates/concept-lineage/fixture.json) and a generated [demo page](../templates/concept-lineage/lineage.html).

## Ownership

- A source owner publishes source records and curated source-to-concept assertions.
- This kit owns the validator, renderer and fictional fixture.
- A consumer owns its own use evidence and pins the public projection by revision and digest. It keeps its own copy of the engine, byte-identical to the kit copy, and fails loudly when the bytes differ.

## What the labels mean

Source quality, local fit, decision, validation and observed benefit stay separate. `Documented source (supplied evidence)` means an origin record with a digest and a matching commit or publication URL was supplied. It does not prove historical code borrowing or adoption. `Origin unresolved; not borrowed` marks a native equivalent whose origin is unknown. A test pairs with a change only on an exact revision match; there is no current-head inference and no ancestry lookup. Shape and hash consistency are not independent publisher authentication.

## Adopting it

Copy `lineage.py` byte for byte, keep its line endings LF (see the literal `.gitattributes` rule in this repository) and pin its SHA-256 and the contract's SHA-256. Run `python3 -m unittest discover -s templates/concept-lineage` before use. Interactive behavior of the page needs a real browser check, which the unit tests do not provide.
