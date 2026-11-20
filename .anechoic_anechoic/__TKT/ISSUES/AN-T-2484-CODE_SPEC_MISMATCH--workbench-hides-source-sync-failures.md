---
identity:
  atom_id: AN-T-2484
context:
  container:
    component: C46
  tier: 3
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-13T19:36:35.200811+00:00'
---
## Summary

Workbench hides source sync failures

## Concern

Workbench discards failed source-status requests. After a poll fails, the status line can keep showing the previous successful sync time without indicating the failure. CA-D-674 requires the read-only status display to show an existing failure. The frontend poll is in `App.svelte` and the status display is in `SyncStatus.svelte`.
