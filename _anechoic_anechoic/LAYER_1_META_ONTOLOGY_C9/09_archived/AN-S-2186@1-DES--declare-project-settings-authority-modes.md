---
atom_family: SPEC
atom_id: AN-S-2186
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

Declare Project.Settings.Authority Modes

## Claim

When this group is authored, both Project Authority Mode and Default Scope Unit Authority Mode are required. Each value is either `strict` or `casual`. An omitted override follows its governed fallback. A local Scope Unit override belongs only to its Project Structure declaration.

```CFEL
Project.Settings.Authority Modes{:0..1}: []{:0};
Project.Settings.Authority Modes.*[in (Default Scope Unit Authority Mode, Project Authority Mode)]{:2}
```
