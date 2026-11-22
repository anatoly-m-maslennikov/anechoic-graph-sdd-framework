---
atom_family: TKT
atom_id: AN-T-2484
container:
  component: C46
priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: resolved
  version: 1
  updated_at: '2026-11-20T20:36:34.866943+00:00'
---
## Summary

Workbench hides source sync failures

## Concern

Workbench discards failed source-status requests. After a poll fails, the status line can keep showing the previous successful sync time without indicating the failure. CA-D-674 requires the read-only status display to show an existing failure. The frontend poll is in `App.svelte` and the status display is in `SyncStatus.svelte`.
