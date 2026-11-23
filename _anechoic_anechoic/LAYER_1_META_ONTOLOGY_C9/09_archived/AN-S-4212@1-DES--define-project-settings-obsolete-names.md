---
atom_family: SPEC
atom_id: AN-S-4212
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 14:16:32 +0400
---
## Summary

Define Project Settings Obsolete Names

## Claim

Project Settings Obsolete Names is the optional collection of registered prior Project names. Each name is a nonempty string. A present empty collection contains no prior names; absence and an explicitly empty collection remain distinct. Exact values and ordering are preserved under CA-D-366, which specifies their TOML representation. This property does not replace the current Project Name or infer additional prior names.

### Formal claim

```text
Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Settings.Obsolete Names[string]{0+}
```
