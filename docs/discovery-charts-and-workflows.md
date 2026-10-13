# StaleToast charts and Breadcrumbs workflows

The public source ledgers remain the archive. StaleToast presents dated Research
and Repository Hot 100 charts. Breadcrumbs presents practical articles from the
public workflow registry, with steps, examples, evidence and correction links.
These are editorial discovery surfaces, not scientific confidence scores or
permission to adopt a workflow.

## Chart editions

The first edition is frozen in
[`staletoast-chart-history/2026-10-12.json`](staletoast-chart-history/2026-10-12.json).
It draws from the source-bound
[`appraisal priorities`](staletoast-appraisal-priorities.md). Research candidates
retain their candidate state. Repository eligibility requires README screening;
portable identity records remain in the full archive.

Order entries by the existing priority key, then stable source ID. Equal
priorities retain their shared group. A display position breaks no evidence tie.
Each edition lists off-chart eligible IDs and the number tied at the cutoff.
The first appearance is NEW. Later editions derive previous position, movement,
peak, re-entry and appearances from recorded editions. An appearance counts an
edition, not a week. Keep frozen editions unchanged.

The site builder ships with the chart interface. It assumes Python 3 and uses
only the standard library. Build the catalog and discovery data with:

```sh
python site/build_priorities.py --check
python site/build_catalogs.py
python site/build_discovery.py
python site/build_discovery.py --check
```

To freeze a later edition, first refresh and review the appraisal projection
against its owning ledgers with `python site/build_priorities.py --write --date
YYYY-MM-DD`. This regenerates both the JSON projection and its Markdown view,
preserving the existing editorial method. Run `python site/build_discovery.py --edition-date
YYYY-MM-DD`, then review the new JSON through a PR. The builder rejects stale
source hashes and changes to an existing dated edition. It does not scout sources,
schedule releases. The priority builder rejects unmatched source/appraisal IDs,
duplicate IDs, malformed rows and unknown claim or appraisal dimensions.

The existing Pages workflow publishes main after direct pushes or a successful
merge-gate run with a current-main PR merged during that run. A skipped merge
does not republish an older release. The resolver uses GitHub.com server records,
checks out the exact main revision and rechecks it before artifact upload. It
does not execute PR code or consume PR build artifacts. Manual main dispatch
remains the recovery path. A successful deployment still needs feature readback
before claiming that a reader's journey works.

Source-link errata live in `staletoast-chart-link-corrections.json`. A correction
binds its dated edition, stable source ID, original URL, corrected URL and pinned
ledger evidence. The builder changes only the derived link and displays a dated
correction note. Frozen edition files, chart positions and evidence states remain
unchanged. The registry checks consistency; the cited source revision provides
the review evidence.

## Workflow articles

The canonical [`workflow registry`](workflow-registry.json) carries article
fields alongside its existing evidence records. Articles explain when a pattern
helps, when to skip it, requirements, steps, a synthetic example, a completion
check and failure modes. Original sources and recorded reproduction dates remain
visible. A local synthetic check does not establish workplace effectiveness.

Submit public discoveries through the workflow discovery issue form. A reviewer
checks source identity, overlap, assumptions, evidence and limitations before
adding an article. Registry 1.1 accepts pinned primary documentation and research
sources under the [versioned source contract](workflow-source-contract.md).
Community records retain their earlier evidence limits. The submission form
does not ingest records automatically.

The daily research and repository scout remains a separate external workflow.
Its unselected leads remain in the
[`next-round pool`](staletoast-next-round-pool.md). Automated workflow scouting
and changes to a consumer's operating practices are not activated by this site.
Consumers can inspect an article and propose a bounded experiment under their
own authority and review process.

## Reusable prompts

The [prompt library](prompt-library.md) and its [machine catalog](prompt-library.json)
cover workflows, data stacks and systems. The discovery builder validates named
inputs, matching synthetic examples, evidence boundaries and source links before
generating the site's searchable prompt data. The site lets a reader copy the
template or fill it with a synthetic example; it makes no model call and stores
no entered context. Editorial review is distinct from model-output evaluation.
