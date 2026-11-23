---
atom_family: SPEC
atom_id: AN-S-4324
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 00:34:40 +0400
---

## Summary

Expose query-inaccessible Atom sources

## Claim

### Prose Claim

The Workbench query Projection must expose a query-visible audit table for every selected Current or Draft Atom source whose declared content cannot be read through `query_run`.

Each row must include the Atom identity when available, the source path, the issue category `query_inaccessible_atom`, and the reader diagnostic or location. A source with no readable Atom row must still be reportable by its path. The table must not expose stale indexed data or repair the source. Readable Atoms remain in the normal query tables.

