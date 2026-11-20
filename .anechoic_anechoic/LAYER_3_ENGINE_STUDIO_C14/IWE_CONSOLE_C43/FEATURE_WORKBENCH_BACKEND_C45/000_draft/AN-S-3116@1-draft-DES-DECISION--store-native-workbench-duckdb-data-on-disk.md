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
  updated_at: "2026-11-20T13:05:31.234323+00:00"
---
## Summary

Store native Workbench DuckDB data on disk

## Claim

### Prose Claim

Store native Workbench DuckDB tables in one Project-local file.
Use the existing Workbench owner and its serialized connection.
Place the working database and spill files in the Workbench runtime directory.
Project sources and the Journal remain authoritative for their facts.

Validate retained data against current sources and configuration before serving queries.
Reuse valid parsed imports and reconcile source changes made while Workbench was stopped.
Use the same file for materialized query results during their temporary lifetime.
Apply the existing paging, pinning, expiry, and restart rules.

Provide an explicit Workbench operation to rebuild one table or all tables.
Rebuild dependent tables by default. Publish affected views and DuckPGQ registration in the same rebuild.
Rerun retained live results when the rebuild includes their tables. Publish a new result ID for each replacement, transfer any open View and its pin, and return old-to-new IDs to standalone callers.
Report failures to stderr and publish no partial rebuild.

## References

[DuckDB runtime storage AN-S-2565](../DEVOPS/AN-S-2565-DEVOPS--deliver-duckdb-atom-content-property-and-relation-records.md), [Single Source of Truth AN-S-348](../../../../LAYER_1_META_ONTOLOGY_C9/DES/AN-S-348-DES--define-single-source-of-truth.md)
