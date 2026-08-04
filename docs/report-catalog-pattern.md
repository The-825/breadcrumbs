# The report catalog: safe self-service data access

## The problem

Non-technical staff need answers out of the data, and the two default paths both fail.
Hand every request to the one person who writes queries, and that person becomes the
queue. Give everyone a query box, and you've handed raw database access to people who
shouldn't have to know what an unbounded join costs, on a surface where one bad query
is an outage or a leak.

## The pattern

A catalog of pre-approved queries behind one generic endpoint, plus a role-gated
escape hatch for the few people who genuinely need more.

- **The catalog is a static map, id to query.** Each report is a parameterized query
  someone technical wrote, reviewed, and keyed by a stable id. Adding a report is a
  code change with review, not a runtime action, so the approved surface only grows
  deliberately.
- **One endpoint runs them all.** A single `/reports/<id>` route looks up the id,
  binds the caller's parameters into the pre-written query (parameterized, never
  string-built), and runs it. New reports don't mean new endpoints; the route logic
  is written once and audited once.
- **Export in the formats people actually use.** CSV and spreadsheet output from the
  same endpoint, because the real consumer of a self-service report is rarely a JSON
  parser. Meeting people where they work is what makes self-service stick.
- **A hard row cap, always.** Every report run is capped server-side. The cap isn't
  about distrust; it converts "someone accidentally requested everything" from an
  incident into a truncated file with a note.
- **The escape hatch is role-gated and separate.** Power users who really do need
  ad-hoc queries get a raw-query path that checks their role explicitly, at the
  boundary, on every call. It's a different door with a different lock, not a flag on
  the shared one, so loosening it for one group can never accidentally loosen the
  catalog for everyone.

## Why not a BI tool

Sometimes a BI tool is the right answer, and this pattern doesn't argue otherwise.
The catalog earns its place when the consumer set is small, the report set is
specific, and the alternative is either a license-per-seat product doing 5% of what
it's priced for, or the one technical person running the same six exports by hand
every week. It's a few hundred lines that removes a human queue, not a platform.

## Adopting it

1. Inventory the recurring requests. The first catalog is just the queries someone
   already runs by hand on a schedule.
2. Write each as a parameterized query with a stable id; review them like any code.
3. Build the one generic route: id lookup, parameter binding, row cap, export
   formats.
4. Add the role-gated raw path only when a real power user actually needs it, not
   preemptively.
