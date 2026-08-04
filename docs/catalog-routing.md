# Catalog routing for a large corpus

> Pairs with `context-budget.md`: that essay prices what a session auto-loads, this
> one is how you keep the rest of a large doc corpus reachable without loading it.

## The problem

Past a certain size, a repo's reference material stops fitting in one rules file.
You end up with dozens of docs, and an agent either re-reads too much of the corpus
every session (expensive, and it still guesses wrong on where the current answer
lives) or under-reads it (fast, and wrong).

## The pattern: three hops, each one narrow

1. **The kernel names a destination class, not a file.** Your top-level rules file
   says "billing questions route to the finance shelf," not a specific path. Classes
   stay stable even as files move.
2. **A catalog maps class to file plus anchor.** One file (or a small set) is the
   card catalog: destination class in, exact file path and section anchor out. This
   is the only place that has to change when you reorganize.
3. **Each file's own header says its neighbors.** The destination file opens with a
   short stamp naming its own sections and the files most likely to be read next
   from here. A wrong hop costs one cheap read of that stamp, not a search of the
   whole corpus.

Each hop is a narrow read: the kernel line, the catalog lookup, the file's own
header. Never all three at once, and never a reconstruction of the whole corpus in
context just to find one fact.

## Why not a flat index

A flat "here's everywhere everything lives" index is the first thing people build,
and it works until the corpus outgrows one screen. Past that, the index itself
becomes the thing nobody keeps current, because every new file is one more line to
remember to add. The three-hop version distributes that maintenance: the catalog
only tracks class-to-file, and each file tracks its own neighbors, so no single file
has to know about the whole tree.

## Adopting it

1. Name your destination classes first, before you have a catalog. If you can't
   name the classes, you don't have enough corpus yet to need this.
2. Build the catalog as a flat lookup table (YAML, a markdown table, whatever your
   agent parses cheaply).
3. Add a short header stamp to each destination file: its own section list plus a
   "nearby" line naming two or three files most often read next from here.
4. When a wrong hop happens, fix the catalog entry, not the kernel. The kernel
   should almost never need to change.
