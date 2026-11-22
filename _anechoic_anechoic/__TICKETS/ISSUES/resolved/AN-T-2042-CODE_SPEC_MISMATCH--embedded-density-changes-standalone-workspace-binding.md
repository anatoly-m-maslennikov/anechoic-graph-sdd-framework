---
atom_family: TKT
atom_id: AN-T-2042
container:
  component: C14
priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: resolved
  version: 1
  updated_at: '2026-11-21T00:54:15.399173+00:00'
---
## Summary

Embedded density changes standalone Workspace binding

## Claim

### Prose Claim

In the ANECHOIC working tree based on `c0b983cb27`, `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/src/App.svelte`, `standaloneContext`, uses `embedded=1` when deciding whether to persist or create a standalone Workspace ID. It also derives the displayed Project name from the URL path. Workspace initialization renders that name without requiring the name returned by Workspace Open or Get. CA-R-2902@9 requires `embedded=1` to set density only and requires the response Project name as the display source. With no explicit Workspace ID, the density marker can change binding and a missing response name is not reported.
