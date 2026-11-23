---
atom_family: SPEC
atom_id: AN-S-2199
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 14:23:38 +0400
---

## Summary

Define Workspace

## Claim

### Formal Claim

```CFEL
Project >{1} Workspace;
Workspace.chat_thread_id [string]{1};
Workspace >{1+} View
```

### Prose Claim

A Workspace is the Project's persistent Workbench context. In this MVP, each Project has exactly one Workspace. The Workspace has exactly one reference to that Project's native persisted app-server thread and one or more Views.

Workspace does not redefine the global Session entity. Multiple Workspace management is out of scope.
