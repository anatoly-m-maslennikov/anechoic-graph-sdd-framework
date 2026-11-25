---
atom_family: SPEC
atom_id: AN-S-1821
container:
  component: C14
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 31
  updated_at: "2026-11-25T23:08:31.999191+00:00"
---
## Summary

Serialize the shared Project Journal

## Claim

### Prose Claim


the shared Project-control Work Journal's serialization.


The shared Project Work Journal **must** retain its ordered event Records outside the Project Graph across restarts and Graph rebuilds.

With `runtime.journal.storage = "files"` (the default), it **must** serialize them as append-only NDJSON File Carrier segments beneath `_journal/` in the selected Project control root or its registered subdirectories.

With `runtime.journal.storage = "duckdb"`, it **must** use a durable standalone Journal table in the Project DuckDB file. Existing NDJSON history **must** be preserved.

These Carriers represent the same Journal, not separate Journals for Scope Units, Content Roles, workflows, or derived log views.

Use the Project database owner for Journal writes. Cross-process producers submit durable staged events to that owner for import in append order. All on-disk tables **must** use the same Project DuckDB file.

## Details

Encode supplied observations safely and read them as recorded. Preserve historical representations and bytes. Report encoding, read, and write failures as observed. Runtime locks and staging state are separate from Journal history. Runtime logs have their own configured sinks.
