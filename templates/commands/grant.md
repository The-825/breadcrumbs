---
description: Capture a standing authority grant in the authority ledger the same turn it lands, or revoke/expire an existing grant (status flip, lines never deleted). Records grants only; never applies labels, never merges.
argument-hint: "<grant scope + source> | revoke G-YYYYMMDD-NN <reason> | expire G-YYYYMMDD-NN <reason>"
allowed-tools: Bash, Grep, Read, Edit
---

Operate on the authority ledger per the schema and lifecycle in `docs/authority-ledger.md` in the companion repo, or your repo's copy of it (read it if you have not this session). Fill these placeholders when installing: `<authority-ledger>` is your ledger path (conventionally `AUTHORITY_LEDGER.jsonl` at the repo root), `<citation-guard>` is your copy of `guard_authority_citations.py`.

The ledger records GRANTS (permissions to act), not facts or rulings: a ruling that states a fact goes to your conclusions store, a durable product decision goes to your decisions ledger, and a statement carrying both a fact and a permission gets captured in both places. Capture is SAME-TURN, per the decision-capture rule: the turn the operator issues the grant is the turn this command writes it down.

Hard boundary: this command WRITES LEDGER LINES AND NOTHING ELSE. It never applies the approval label, never merges a PR, and never edits any merge-gate file. Recording a merge-authority grant does not make anything merge; only the merge gate, reading the ledger from the base branch, can act on one.

Parse **$ARGUMENTS**:

## If it starts with `revoke` or `expire` followed by a grant id

1. Locate the line: `grep -n '"id": "<the id>"' <authority-ledger>` (match with and without the space after the colon). If absent, stop and say so.
2. Flip `"status": "active"` to `"status": "revoked"` (or `"expired"`) on that line via Edit, and append to its `notes` value: `Revoked <today YYYY-MM-DD>: <reason>` (or `Expired ...`). Never delete or reorder lines; never touch any other field or line.
3. Validate the edited line still parses: `python3 -c "import json; [json.loads(l) for l in open('<authority-ledger>') if l.strip()]" && echo LEDGER-OK`.
4. Echo the updated line back to the operator.

## Otherwise: capture a new grant

1. Compute the next id for today (`date +%Y%m%d`): find the highest existing sequence for today's date in `<authority-ledger>` and increment; start at `01` when there is none.
2. Build the JSON object with every schema field: `id`, `date` (today), `scope` (from $ARGUMENTS, specific enough to check an action against), `wording` (the operator's VERBATIM words ONLY if the conversation or cited source contains a true verbatim quote; otherwise `null`. Never invent a quote or paraphrase-as-quote), `source` (REQUIRED pointer: session + date, PR number, rules-file section, or decisions-ledger entry; if $ARGUMENTS gives none, use the current session + today), `expiry` (`null` unless a bounded grant was stated), `status` (`"active"`), `issued_to`, `notes`.
3. Merge-clearing grants ONLY, and only if your merge gate has been wired to read the ledger (Phase 2 in `docs/authority-ledger.md`; the companion kit ships that contract as documentation, not gate code): ask the operator which wait site the grant clears, then add the machine fields: `grant_type` (`"merge-authority"`), `applies_to` (the one wait site), `paths` (list of globs; required for path-scoped grants: every changed file in a citing PR must match one), `until` (`YYYY-MM-DD`; required for window grants). Skip all four for documentation-only grants; without `grant_type: "merge-authority"` a citation never affects merging. Remind the operator: no grant clears a PR that touches the merge gate's own machinery; those always need the approval label.
4. Validate BEFORE appending. Write the candidate line to a temp file and require `python3 -c "import json; json.loads(open('<tmp>').read())"` to pass; on failure, fix the line. Never append a broken line.
5. Append it: `cat <tmp> >> <authority-ledger>` (single trailing newline), then confirm the whole ledger passes the guard: `python3 <citation-guard> --ledger <authority-ledger> --sweep`.
6. Echo the appended line back to the operator, and note that PRs acting under it may cite it with a PR-body line `Authority: <id>`.

If the same statement also settled a fact, capture that fact in the conclusions store as its own entry; do not fold facts into grant lines.
