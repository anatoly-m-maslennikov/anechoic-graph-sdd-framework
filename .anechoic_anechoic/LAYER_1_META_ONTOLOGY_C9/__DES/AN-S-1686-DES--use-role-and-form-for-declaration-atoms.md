---
atom_family: SPEC
atom_id: AN-S-1686
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Use Role and Form for Declaration Atoms

## Claim

### Prose Claim


The proposed authored representation and formal paths of a Node Declaration.


The proposed Atom schema **must** distinguish Role from Form. The current Atom `content_role` field maps to the proposed `role` value, and the current `type` field maps to the proposed `form` value. A Declaration Atom has `role: Requirement` and `form: Declaration`; Declaration is a Form under the Requirement Role, not a new Role value. In Subject addresses, express that pair as `Atom/(.Header.Role := Requirement)/(.Header.Form := Declaration)`. Use `Form` for the form qualifier in place of a legacy nested `Role: X` or `Type: X` qualifier.

Role identifies the contribution. Form identifies its authoring form and does not override or duplicate Role.
