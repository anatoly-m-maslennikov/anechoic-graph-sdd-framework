---
identity:
  atom_id: AN-S-1967
context:
  container:
    component: C43
  tier: 4
  lens: SWD
state:
  status: draft
  version: 4
  updated_at: '2026-11-14T07:53:24.803459+00:00'
---
## Summary

Reuse canonical carrier validation for audits

## Claim

### Prose Claim

Reuse canonical carrier validation, the source reader, and locator for audits.
Audit the selected inventory, including loaded Archives.

## Details

- Coalesce audits after commit, outside the lifecycle response path.
- Prepare only affected paths and required context for ordinary deltas.
- Publish the latest diagnostics for each path. Measure audit time separately.
