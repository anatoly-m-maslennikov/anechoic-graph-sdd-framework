---
atom_family: SPEC
atom_id: AN-S-2260
structure:
  container:
    component: C45
  tier: 4
context:
  lens: SWD
state:
  status: active
  version: 1
  updated_at: '2026-11-13T16:24:47.409913+00:00'
---
## Summary

Use one saved SQL store for Load and Recent

## Claim scope

Workbench backend reads of Bookmarks and saved Views.

## Claim

### Prose Claim

Use the saved SQL store in `saved_queries.py` for both Load and Recent. Load resolves the ID or URL and returns the stored SQL verbatim. Recent reads the same store and returns the saved ID, kind, optional name, preview and saved time.