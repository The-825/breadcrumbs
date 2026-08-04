# Decisions ledger template

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

A ruling that lives only in a transcript gets re-litigated. Worse, a session that never saw it ships work that quietly contradicts it. The decisions ledger is the counter: an append-only file where every durable ruling (a price, a name, a threshold, a policy call) lands the same turn it is made. Same turn, not end of session, because a session can end or compact before any summary gets written. Capture on the event beats capture on a schedule.

## The format

```markdown
# DECISIONS.md · decisions ledger

One entry per durable ruling, newest last. Append the entry the SAME turn the
ruling lands, before moving on to the work it unblocks. Superseded entries stay
in the ledger with a "Superseded by D-<n>" line added. Never silently rewrite
an entry.

## D-<n> · <date> · <topic>
Ruling: <the decision, one or two sentences>
Why: <one line of rationale>
Source: <where it landed: session, PR #, email>
```

Two example entries, the shape to copy:

```markdown
## D-4 · 2026-03-02 · Membership pricing
Ruling: Annual membership launches at $79, monthly at $9. No founding-member
discount tier.
Why: Annual under $80 tested better than a discount ladder, and one price is
easier to defend in copy.
Source: Pricing session, 2026-03-02.
Superseded by D-9.

## D-5 · 2026-03-11 · Revenue dashboard naming
Ruling: The executive dashboard is titled "Revenue Overview", not "Sales
Dashboard". "Revenue" everywhere it appears: nav, page title, exports.
Why: Finance and sales argued over "sales"; "revenue" matches the ledger the
numbers come from.
Source: PR #41 review thread.
```

## The rebuild variant: decisions paired with the failures they prevent

The same file takes a second shape when it is founding a rebuild instead of logging rulings as they land. Each row pairs a day-one decision with the specific debt or incident in the old system it prevents. That pairing is the point: abstract rules are easy to ignore, and a rule traced to a named failure earns its place. Filling in the right column doubles as a retrospective of the system you are replacing.

Copy the tables below, keep the left column (delete any decision that does not fit your stack), and replace every right-column prompt with your own evidence. Be specific: name the file, the number, the outage, the week lost. If you cannot name a failure a decision prevents, question whether the decision belongs in your list.

A filled row looks like this (anonymized, from a real production system):

| Decision | What it avoids in the old system |
|---|---|
| Modular frontend, one module per view, from day 1 | The old frontend grew into a single-file classic script around 19,000 lines; the decomposition plan kept outrunning itself because extraction started years too late. |

```markdown
## Architecture (structure from commit 1, not retrofitted)

| Decision | What it avoids in <old-system> |
|---|---|
| Modular frontend, one module per view, from day 1 | *What monolith did the old frontend become, and when did extraction start?* |
| App factory + per-area route modules + shared helpers from day 1 | *Did the old backend start as a single file? When was it decomposed, and what did the delay cost?* |
| One version-controlled database view layer | *Did views exist only in a console? Did any drift from their checked-in DDL?* |
| Data-quality assertions wired into a real run gate | *Were assertions compile-only? Did any ever run against production?* |
| Feature flags on one store, fail-closed uniformly, from day 1 | *Did flags live in two stores? Did any flag fail open on exception?* |
| Central config registry from day 1 (one frozen dataclass, every env var and threshold in it) | *Where were the magic numbers scattered? What inline literals survived the retrofit?* |
| CI-stamped version strings, never hand-bumped | *What drifted when versions were hand-edited in two places?* |
| Migration runner (tracks applied-per-tenant, refuses duplicate numbers and out-of-order apply) | *What numbering collision or out-of-order apply reached your database from a loose folder?* |
| ADR directory from day 1 | *Which architectural decision can nobody explain anymore?* |

## Testing and CI (floor before features)

| Decision | What it avoids in <old-system> |
|---|---|
| CI lint guards from the first PR | *What convention decayed for months before a guard stopped the re-creep?* |
| Test-gated deploys from the first deploy | *Did a red test ever fail to block a rollout? What shipped broken?* |
| Route-integration harness + render-the-view smoke from day 1 | *What bug returned 200 from the route but rendered an empty page?* |
| Browser e2e suite from day 1 | *What runtime regression class forced the retrofit?* |
| API spec discipline, prefer generated over hand-curated | *Did the hand-curated spec drift as routes evolved?* |

## Data model (design-in, not patch-in)

| Decision | What it avoids in <old-system> |
|---|---|
| Typed ingestion, no schema autodetect, plus a null-rate quarantine that refuses a degraded write | *Did an autodetect load ever silently null out or re-type columns at scale?* |
| Never rebuild a canonical store from a side snapshot or spreadsheet | *Did a rebuild-from-snapshot ever resurrect deleted state?* |
| Soft-delete recoverability as the load-bearing wall | *What longitudinal analysis is only possible because records never disappear?* |
| Stamp the real domain event, not the sweep date | *Did a batch-sweep timestamp masquerade as the event date and break an analysis?* |
| Blank-is-not-missing encoded in the data dictionary at schema time | *Which presence-flag or categorical fields were misread as "mostly missing"?* |
| Reconcile stated intent against observed behavior as first-class | *Where did a silent "no" (a form nobody was required to submit) distort a denominator?* |
| One writer per field; resolver-owned columns excluded from bulk upserts | *Did a re-pull ever wipe hand-resolved values? What did resolution coverage do once you excluded them?* |
| Incremental watermark on a reliable field | *Which timestamp field turned out to be unreliable, and what did syncing on it miss?* |
| Stable-key table naming, never a mutable slug | *Did renames ever spawn duplicate tables via slug drift?* |
| Operator-set current-period singleton, never derived from the clock | *Did calendar logic baked into code go stale until a redeploy?* |
| Resolve identity to a canonical key before comparing aliases | *How many "changes" were the same person under different aliases or typos?* |

## Process

| Decision | What it avoids in <old-system> |
|---|---|
| Source-inventory gate before any multi-source aggregation | *What surface got built on the first source reached and missed the rest?* |
| Batch-push cadence + feature-slug branches | *Did work ever land on a session-named or auto-generated branch?* |
| Capture a semantic ruling the same turn it lands | *Which ruling lived only in a transcript and got re-litigated or silently violated?* |

## Build order (the meta-lesson)

*Fill this section in prose. The pattern to look for: the old system built
features first and the force-multiplier floor second, so config registries,
flags, the view layer, e2e tests, the API spec, the test harness, and module
decomposition all arrived as retrofits. The rebuild inverts that order: lay the
floor first, then the data spine, then compose features on the patterns. State
your own version of that verdict here, with whatever evidence your
retrospective produced, and link your build-order doc.*
```

## Adoption notes

The bar for a ledger entry is durability, not importance. If a future session could plausibly redo the debate, it goes in. The Superseded line is what keeps the ledger honest: the old ruling stays visible with its reasoning, so you can always see what changed and why, and nobody wonders whether an entry was quietly edited.

The rebuild variant has the same honesty test in the other direction: every decision must point at a real failure. Neutralize or delete the rows that do not apply to your stack rather than leaving prompts unanswered; an unfilled right column is a decision you have not actually justified.

An entry costs thirty seconds. Re-litigating the same decision costs an afternoon, and sometimes it costs the decision.
