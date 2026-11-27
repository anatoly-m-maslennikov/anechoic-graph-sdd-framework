---
atom_family: TKT
atom_id: AN-T-2049
container:
  component: C14
priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: resolved
  version: 1
  updated_at: '2026-11-21T00:54:50.445245+00:00'
---
## Summary

Workbench can show an old Check verdict after a new failure

## Claim

### Prose Claim

CA-M-466@9 requires truthful stale and error states. `FEATURE_IWE_CONSOLE_FRONTEND/src/App.svelte` keeps and displays the previous Check verdict across a query edit and a failed Check. A View can show a Valid verdict alongside an error for the current query.
