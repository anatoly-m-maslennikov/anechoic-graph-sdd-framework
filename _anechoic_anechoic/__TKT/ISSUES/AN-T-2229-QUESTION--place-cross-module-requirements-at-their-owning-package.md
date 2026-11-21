---
atom_family: TKT
atom_id: AN-T-2229
structure:
  container:
    component: C45
  priority: 2
context:
  template: question
state:
  status: active
  version: 1
  updated_at: '2026-11-13T15:59:15.894221+00:00'
---
## Summary

Place cross-module Requirements at their owning Package

## Concern

How should the pilot trace a Requirement whose behavior is split across several Modules? CA-R-2727@20 spans `App.svelte` and `ViewTabs.svelte`; CA-R-2776@10 spans `App.svelte` and `SavedPanel.svelte`. Pinning both Requirements in every contributing Module produces many-to-many links. The reviewed policy allows a shared Claim to be pinned once in the smallest owning Package. Should the pilot use that rule for this cluster and reserve Module pins for independently implemented Claims?