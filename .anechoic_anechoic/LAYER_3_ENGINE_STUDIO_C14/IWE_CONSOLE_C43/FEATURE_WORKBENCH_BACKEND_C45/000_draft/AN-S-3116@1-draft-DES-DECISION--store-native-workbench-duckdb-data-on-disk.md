---
identity:
  atom_id: AN-S-3116
context:
  container:
    component: C45
  tier: 1
  lens: DES
  template: DECISION
state:
  status: "draft"
  version: 1
  updated_at: "2026-11-20T15:54:00.998793+00:00"
---
## Summary

Store native Workbench tables in one Project-local DuckDB file. Use the
existing serialized connection and keep the database and spill files in
the Workbench runtime directory. Project sources and the Journal remain
authoritative for their facts.

Validate retained data before serving queries. Reuse valid parsed imports
and reconcile changes made while Workbench was stopped. Store live results
in the same file and apply the existing expiry, pinning, and startup rules.

Rebuild one table or all tables on demand, including dependent tables.
Replace affected snapshots and keep their Views and pins attached. Return
the replacement IDs. Report failures to stderr and the requesting client.
Roll back failed SQL writes. Require an explicit restart if failure may
have lost graph registration. A second writer exits with a lock error.

## References

[DuckDB runtime storage AN-S-2565](../DEVOPS/AN-S-2565-DEVOPS--deliver-duckdb-atom-content-property-and-relation-records.md), [Single Source of Truth AN-S-348](../../../../LAYER_1_META_ONTOLOGY_C9/DES/AN-S-348-DES--define-single-source-of-truth.md)
