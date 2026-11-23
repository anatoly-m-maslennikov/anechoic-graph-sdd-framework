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
  version: 3
  updated_at: 2026-11-09 00:09:26 +0400
---

## Summary

Define Workspace

## Claim

### Prose Claim

A Workspace is the Workbench context for one selected Project. In an existing native Codex chat, it binds to the host-supplied native thread reference; that reference is required only in native mode and is never invented or reused from another chat. In standalone browser mode, it uses the existing browser-owned Workspace/session ID without a native chat or an invented native thread reference. It keeps at least one View. It does not create a second conversation history or a standalone chat.
### Formal Claim

```CFEL
Workspace.native_thread_id [string]{0..1};
Workspace.project_root [string]{1};
Workspace >{1+} View
```

