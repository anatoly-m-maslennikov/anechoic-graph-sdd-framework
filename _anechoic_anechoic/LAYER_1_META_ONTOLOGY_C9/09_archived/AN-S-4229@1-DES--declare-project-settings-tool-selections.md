---
atom_family: SPEC
atom_id: AN-S-4229
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

Declare Project.Settings.Tool Selections

## Claim

Encode selected active and background Tools with their per-Tool settings.

```CFEL
Project.Settings.Tool Selections{:0..1}: []{:0};
Project.Settings.Tool Selections.*[string]{:0+}
```
