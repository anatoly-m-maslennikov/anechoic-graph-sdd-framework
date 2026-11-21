---
atom_family: TKT
atom_id: AN-T-2067
container:
  component: C14
priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-12T12:59:04.618389+00:00'
---
## Summary

Host graph generation scans Atom source folders

## Claim

### Prose Claim

CA-M-1006@7 requires targeted Workbench queries for Atom reads and limits direct file reads to selected targets. `FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/current_entity_sources.py` inventories folders and reads Atom files directly for the host graph commands. The review found no separate exception for those commands. Workbench indexing and offline image bootstrap have their own input boundaries.
