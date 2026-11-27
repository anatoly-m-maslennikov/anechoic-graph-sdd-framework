---
atom_family: SPEC
atom_id: AN-S-2261
container:
  component: C46
tier: 4
context:
  lens: SWD
state:
  status: active
  version: 1
  updated_at: '2026-11-13T16:24:31.077676+00:00'
---
## Summary

Render Workbench View tabs in one component

## Claim scope

The tab strip in the Workbench frontend.

## Claim

### Prose Claim

Use `ViewTabs.svelte` to render the tab strip and its controls. Pass selection, close, rename and duplicate requests to the Workspace handlers with the selected View ID. Pass New View to the create handler.