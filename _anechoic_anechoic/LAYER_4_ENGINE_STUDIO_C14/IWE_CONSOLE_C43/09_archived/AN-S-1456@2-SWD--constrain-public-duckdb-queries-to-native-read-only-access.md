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
  version: 2
  updated_at: 2026-11-04 00:38:14 +0400
---

## Summary

Constrain public DuckDB queries to native read-only access.

## Claim scope

Public SQL access to the in-memory DuckDB Projection.

## Claim

### Prose Claim

Public SQL access to the in-memory DuckDB Projection must use `connection.extract_statements(sql)` to parse the submitted SQL with DuckDB's native engine. It accepts exactly one Statement whose native StatementType is `SELECT`, then executes the original exact SQL once through that same connection. It rejects multiple Statements and every other StatementType, including DDL, DML, `SET`, `COPY`, and `ATTACH`.

This boundary must not use a regular-expression keyword check or `from_query`, which can execute DML.

Before public SQL is accepted, trusted setup must disable external access, lock configuration, and register only pure query helpers with no mutation effect. Public SQL must not be able to enable external file or network access.

Trusted setup creates only the two public tables and no Sequences. It must configure an empty temporary directory and verify, in the selected DuckDB runtime, that temporary spilling is disabled. The in-memory Projection creates no database, snapshot, schema, or log files.

Public SQL does not write Atom carriers or the Projection. Runtime acceptance must prove that an embedded write attempt is rejected.
