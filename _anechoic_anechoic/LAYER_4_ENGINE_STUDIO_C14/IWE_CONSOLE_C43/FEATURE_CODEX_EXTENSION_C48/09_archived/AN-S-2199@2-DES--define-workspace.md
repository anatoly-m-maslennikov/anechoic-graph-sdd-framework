---
atom_family: SPEC
atom_id: AN-S-2199
container:
  component: C48
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-05 16:45:35 +0400
---

## Summary

Define Workspace

## Claim

### Prose Claim

A Workspace is the Workbench context for one existing native Codex chat in one selected Project. It keeps one native thread reference and at least one View. It does not create a second conversation history or a standalone chat.
### Formal Claim

```CFEL
Workspace.native_thread_id [string]{1};
Workspace.project_root [string]{1};
Workspace >{1+} View
```

