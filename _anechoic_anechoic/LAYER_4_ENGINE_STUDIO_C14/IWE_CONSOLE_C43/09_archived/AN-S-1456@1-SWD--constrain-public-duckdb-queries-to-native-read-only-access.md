---
atom_family: SPEC
atom_id: AN-S-1456
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

Constrain public DuckDB queries to native read-only access.

## Claim scope

Public SQL access to the DuckDB Projection.

## Claim

### Prose Claim

Public SQL access to the DuckDB Projection must use DuckDB's native read-only connection mode. It must not rely on a SQL keyword check.

Before public SQL is accepted, the owner must disable external access and lock its configuration. Public SQL must not be able to re-enable external file or network access.

These constraints apply together:

- native read-only mode prevents Projection changes, including writes nested in a WITH query;
- disabled external access prevents unrelated file and network access; and
- trusted setup registers only the ANECHOIC helpers required by public SQL before the read-only query mode is opened.

Public SQL does not write Atom carriers or the Projection.
