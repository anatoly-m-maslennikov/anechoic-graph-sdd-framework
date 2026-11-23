---
atom_family: SPEC
atom_id: AN-S-2535
container:
  component: C43
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-11-03 23:17:14 +0400
---

## Summary

Preserve governed Atom data and reuse native SQL.

## Claim scope

The reader and query semantics of the DuckDB Projection.

## Claim

### Prose Claim

The DuckDB Projection reader must use the governed source inventory and canonical Atom carriers. It must preserve the source locator and source bytes, complete parsed Header, original frontmatter text, and unchanged Markdown body for every valid carrier.

The reader must retain mapped Content Properties as separate direct Markdown and complete section Markdown values, with their paths, parent paths, headings, levels, and positions. It must use real Markdown heading structure and preserve source formatting.

The synchronizer must use the existing stable-read and parsing functions as per-source leaf mechanics. Its collector must return a per-source valid capture or an excluded source-file error; it must not reuse the existing whole-inventory Atom Read/Query collector as-is or weaken that collector's separate public contract.

Invalid, unreadable, and changed-during-capture source data must be omitted from the Projection with its owned derived rows. The collector reports the source path, error, and available error location only to stderr, skips that input, and continues with other valid sources. It must never retain stale rows for the affected source, return diagnostics as query rows, repair the source, or automatically resubmit the same failed input. A later actual file edit, move, or new observed source state is a new input.

Use DuckDB as the SQL engine and reuse its native SQL behavior. The only ANECHOIC graph extension is the minimal `expand` helper over indexed registered Relation Types: it resolves an unambiguous seed, follows selected directions, includes each reachable reference once, terminates cycles, and returns references rather than embedded objects. The Projection does not add a SQL-like parser or evaluate Formal Claims.
