---
atom_family: SPEC
atom_id: AN-S-1821
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 30
  updated_at: "2026-11-25T21:12:23.096775+00:00"
---
## Summary

Serialize the shared Project Journal

## Claim

### Prose Claim


the shared Project-control Work Journal's serialization.


The shared Project Work Journal **must** retain its ordered event Records outside the Project Graph across restarts and Graph rebuilds.

With `runtime.journal.storage = "files"` (the default), it **must** serialize them as append-only NDJSON File Carrier segments in `.anechoic_<project_name>/_journal/` or its registered subdirectories.

With `runtime.journal.storage = "duckdb"`, it **must** use a durable standalone Journal table in the Project DuckDB file. Existing NDJSON history **must** be preserved.

These Carriers represent the same Journal, not separate Journals for Scope Units, Content Roles, workflows, or derived log views.

Workbench **must** own the Project DuckDB file. Cross-process writers **must** submit durable staged events to Workbench, which imports them into the Journal in append order. All on-disk tables **must** use the same Project DuckDB file.

## Details

This serialization governs the Project-control Work Journal, not every runtime technical or business Journal. Runtime Journal Delivery may use configured local or remote databases and logging sinks.
