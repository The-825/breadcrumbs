# StaleToast and Breadcrumbs ownership

StaleToast owns collaborative-intelligence research and repository catalogs,
source appraisals, daily discovery, the retained pool, editorial priorities and
frozen chart history. [Repository](https://github.com/The-825/staletoast) and
[site](https://the-825.github.io/staletoast/).

Breadcrumbs owns practical workflow guides, reusable prompts, implementation
templates and the agent-operations kit. It consumes evidence from StaleToast;
a source screen or chart position never grants consumer adoption authority.

## Migration and compatibility

The initial StaleToast import preserves selected-path Git history, original
authors and 52 relevant historical commits. Its migration provenance records
the original Breadcrumbs revision and exact source hashes. Stable source and
claim IDs, all source records and both frozen chart editions are preserved.

Breadcrumbs' old research files remain a read-only migration archive. They are
not the active intake destination. CLI writes through the legacy landscape,
promotion, triage, priority and chart entrypoints are refused after the split.
Read-only archive checks remain available so historical evidence can be verified.
Nothing was deleted from the original repository.

Old chart, research, repository, claim, source-detail, synthesis and method URLs
route to the same pages in StaleToast, preserving query strings and fragments.
Readers without JavaScript retain the archived page and explicit links to the
new owner. Workflow, prompt, starter and implementation pages remain here.

## Consumer build

Python 3.9 or newer, standard library only. `staletoast-consumer.json` pins one
permanent StaleToast export URL, source revision and SHA-256 digest. The source
owner publishes append-only snapshots under `exports/<catalog-revision>.json`.
Website-only updates and squash merges do not change a catalog's exact input
binding. Earlier snapshots remain available after later editions publish.

The consumer rejects wrong owners, unexpected URLs, mismatched revisions or
digests, invalid identities and a transfer that tries to take workflow or
prompt ownership. It never falls back to the archived local research ledgers.
A cache is accepted only after the same pin and integrity checks.

Existing build commands still work: the catalog and chart stages use the
checked export, while workflow and prompt catalogs use their native registries.
To update the consumed snapshot, review the new export, update URL/revision/digest
together, and verify the complete build before release. Do not silently switch
to latest. Cross-links route readers to StaleToast's current published charts.

## Daily scout

The existing daily 9 AM Pacific scout retains its schedule and coordination
target. Research/repository ingestion and ranking now run in StaleToast's owning
checkout and review gate. Workflow and prompt proposals remain under Breadcrumbs'
review boundary. Deduplicate against StaleToast's uncapped ledgers, aliases,
dated intake receipts and retained pool. Target one to two research articles and
one to two repositories per day at defensible evidence depth; document shortfalls
instead of filling quotas. Unselected leads remain in the pool.

Source discovery, editorial ranking, synthetic rehearsal, measured runtime use
and adoption remain separate. Public and synthetic data only. No private records
or production state crosses this catalog boundary.
