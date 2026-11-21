---
atom_family: TKT
atom_id: AN-T-2484
structure:
  container:
    component: C46
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: draft
  version: 2
  updated_at: '2026-11-13T20:54:41.342172+00:00'
---
## Summary

Workbench hides source sync failures

## Concern

Workbench discards failed source-status requests. After a poll fails, the status line can continue to show the previous successful sync time without indicating the failure. CA-D-674 requires the read-only status display to show an existing failure. The frontend poll is in `App.svelte`; the status display is in `SyncStatus.svelte`.
