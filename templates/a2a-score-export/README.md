# A2A Breadcrumb Score extension

Attach a published, human-reviewed Breadcrumb Score pointer to an A2A 1.0 Agent Card as a non-required capability extension.

The standard-library exporter validates a public card, requires an unexpired publication-approved assessment, recomputes its digest, and refuses signed cards, local endpoints, unknown top-level fields, drafts, and mismatched targets. The provider must re-sign any modified signed card.

It does not collect evidence, publish files, sign cards, host endpoints, or grant trust. Keep authenticated Agent Card fields out of the public input.

Run `python3 -m unittest discover -s tests` from this directory.
