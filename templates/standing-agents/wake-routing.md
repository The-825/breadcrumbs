# Wake routing

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

A merge changes files a specialist desk owns, and nobody tells the desk. The drift sits until the next summon stumbles over it mid-task, which is the most expensive possible moment to discover it. Wake routing closes the loop: after each merge, map the changed paths to the desks that own them and notify each one. Use it as soon as your registry has desks with real path scopes; the registry and the rest of the fleet kit are indexed in the [README](README.md).

The route table and router, copy and adapt:

```python
# Longest matching prefix wins, so a desk can own a subtree inside
# another desk's tree. Keep desk ids identical to the registry's.
ROUTES = [
    ("pipelines/",         "desk-data-pipeline"),
    ("warehouse/",         "desk-data-pipeline"),
    ("dq/",                "desk-data-pipeline"),
    ("web/",               "desk-frontend"),
    ("deploy/",            "desk-ops"),
    ("ops/",               "desk-ops"),
    (".github/workflows/", "desk-ops"),
]

def desks_for_paths(changed_paths, routes=ROUTES):
    """Map changed repo-relative paths to the desk ids that own them."""
    hits = set()
    for path in changed_paths:
        p = str(path or "").strip()
        if p.startswith("./"):
            p = p[2:]
        best, desk = "", None
        for prefix, d in routes:
            if p.startswith(prefix) and len(prefix) > len(best):
                best, desk = prefix, d
        if desk:
            hits.add(desk)
    return sorted(hits)
```

## The routing rule

Most specific wins: the longest matching prefix beats a shorter one, so `web/` can belong to the frontend desk while a `web/api-client/` row routes that subtree elsewhere. A path matching nothing wakes nobody, and that silence is a designed signal: either the table is missing a row or the path genuinely has no specialist, and a periodic sweep of unmatched paths tells you which.

## Where it hooks

Two placements; pick one to start:

- **CI on merge to the default branch.** A small job runs `git diff --name-only` over the merged range, feeds the list to the router, and notifies each hit: file a task on the bus routed to the desk, or poke the desk's standing session if one is up. This is the tight loop; drift is announced within minutes of landing.
- **A scheduler.** A nightly job diffs the day's merges and files one digest task per desk. Cheaper and calmer; fine when same-day is fast enough.

Either way the notification is a bus task, not a direct edit: the desk decides what the change means for its area, on its own boot diet.

## Keeping the table true

The table is a second copy of ownership facts the registry already holds, so give it a drift check: a few asserting lines in CI that every desk id in ROUTES exists in the registry, and every registry desk with paths appears in ROUTES. Better, generate ROUTES from the registry's `scope.paths` at run time and that drift class disappears entirely; the inline table above is the starting form, not the destination.

Routing is cheap; rediscovery is not. Thirty lines of prefix matching buys every merge a specialist who heard about it.
