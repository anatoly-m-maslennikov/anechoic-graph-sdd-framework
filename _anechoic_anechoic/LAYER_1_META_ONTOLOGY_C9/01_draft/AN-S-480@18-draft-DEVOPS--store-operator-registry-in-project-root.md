---
atom_family: SPEC
atom_id: AN-S-480
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: draft
  version: 18
  updated_at: 2026-11-05 13:47:13 +0400
---
## Summary

Store Operator Registry in Project Root

## Claim

### Prose Claim


the authoritative Operator registry of a Project.


the authoritative Operator registry **must** use **`=1`** `operators_registry.toml` file **in** the Project authority root, alongside Project Settings.

- the root has **`=1`** key, `operators`, containing **`>=1`** `[[operators]]` table.
- **every** table has **`=1`** `name` **and** **`=1`** `role`, both nonempty strings. names are unique. additional keys **or** duplicate identities make the registry invalid.
- `role` describes the Operator; it does **not** replace the name **or** independently grant execution permission.
- concrete Operator names **and** roles belong **only** **in** the Project's registry, **not** **in** reusable methodology **or** Tool code. a missing, unreadable, malformed, **or** stale registry leaves membership unresolved; it is **not** an empty valid registry.

