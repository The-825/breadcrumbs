# Union merges for append-only ledgers

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

## The problem

An append-only jsonl ledger has one hot spot: the end of the file. Two parallel sessions each append an entry on their own branch, and both PRs now touch the same final lines. Every pair of appending branches conflicts, even though both changes are legitimate and the correct resolution is always the same: keep both lines. On a repo where several agent sessions run at once, the conclusions ledger becomes the most-conflicted file in the tree for no real reason.

## The one-line fix

```
CONCLUSIONS.jsonl merge=union
```

One line in `.gitattributes` at the repo root (adjust the path to wherever your ledger lives). `union` is a built-in git merge setting, no driver configuration needed: on a conflicting hunk it keeps both sides' lines instead of emitting conflict markers. For a file where every line is an independent record and edits are pure appends, that is exactly the right resolution, every time.

## The honest limit

GitHub's pull request mergeability check does not honor merge attributes. Two PRs that both append will still show as conflicted on GitHub, and the merge button will still refuse. What the attribute buys is that the local fix becomes fully mechanical, with zero hand-editing:

```
git fetch origin main && git merge origin/main && git push
```

The merge auto-resolves via union, the push updates the PR, and any merge automation re-evaluates on the new commit. Without the attribute, the same conflict drops you into hand-editing conflict markers inside a jsonl file, which is exactly where a tired human duplicates a brace and breaks a line.

## When union is unsafe

Union applies the "keep both" rule blindly and silently, with no conflict markers to review. Declare it only for files where that rule is always correct. Do not declare it for:

- **Files with same-line edits.** Any file where an update rewrites an existing line in place: a "next free number" line, a counter, a status field. Union keeps both versions of the edited line, and the file now quietly carries a duplicate.
- **Files that ever receive redaction edits.** If a scrub (removing a leaked secret or a name) races an append, union can resolve the conflict by keeping the removed lines. A file where deletion must stick is a file where union must not decide.
- **Ordered prose.** Docs where line order and section structure carry meaning. Union can interleave or duplicate hunks, producing a file that parses as text and reads as nonsense.

Before declaring union on a ledger, check that its history really is append-only: `git log -p -- CONCLUSIONS.jsonl` should show additions only. A file that has already needed in-place fixes will need them again.

## One interaction to know about

The provenance extension ([PROVENANCE.md](PROVENANCE.md)) sanctions exactly one in-place edit: refreshing an entry's `verified` date. A refresh racing an append is fine, since they touch different lines. But if two branches refresh the same entry's `verified` date to different values, union keeps both versions of that line and the entry is duplicated. It is a rare collision and easy to spot (two lines identical except the date; keep the newer), but it is the one way the sanctioned edit can bite under union, so treat a duplicated entry as a hand-fix signal, not corruption.
