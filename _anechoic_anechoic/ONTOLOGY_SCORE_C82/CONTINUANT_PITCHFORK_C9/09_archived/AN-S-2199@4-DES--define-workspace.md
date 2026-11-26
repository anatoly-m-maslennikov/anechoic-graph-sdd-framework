---
atom_family: SPEC
atom_id: AN-S-2199
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Define Workspace

## Claim

### Prose Claim

A Workspace is the Workbench context for one selected Project. In an existing native Codex chat, it binds to the host-supplied native thread reference; that reference is required only in native mode and is never invented or reused from another chat. In standalone browser mode, it uses the existing browser-owned Workspace/session ID without a native chat or an invented native thread reference. It keeps at least one View. It does not create a second conversation history or a standalone chat.
### Formal Claim

```CFEL
# model
Workspace.native_thread_id{::0..1}:: [string]{::0..1};
Workspace.project_root{::1}:: [string]{::1};
View {::1}((IS_CONTAINED_BY)){::1+} Workspace
```

