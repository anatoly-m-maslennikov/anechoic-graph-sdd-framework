---
atom_family: SPEC
atom_id: AN-S-4228
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 08:06:47 +0400
---

## Summary

Declare Project.Settings.Extension Selections

## Claim

Encode enabled and disabled installed Extensions. Retain the selected revision when applicable and retain per-Extension settings. Retained settings do not activate a disabled Extension.

```CFEL
Project.Settings.Extension Selections{:0..1}: []{:0};
Project.Settings.Extension Selections.*[string]{:0+}
```
