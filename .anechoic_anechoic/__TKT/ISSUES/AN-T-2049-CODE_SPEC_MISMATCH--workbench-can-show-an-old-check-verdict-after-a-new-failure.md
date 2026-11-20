---
atom_family: TKT
atom_id: AN-T-2049
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:53:27.079173+00:00'
---
## Summary

Workbench can show an old Check verdict after a new failure

## Claim

### Prose Claim

CA-M-466@9 requires truthful stale and error states. `FEATURE_WORKBENCH_FRONTEND/src/App.svelte` keeps and displays the previous Check verdict across a query edit and a failed Check. A View can show a Valid verdict alongside an error for the current query.
