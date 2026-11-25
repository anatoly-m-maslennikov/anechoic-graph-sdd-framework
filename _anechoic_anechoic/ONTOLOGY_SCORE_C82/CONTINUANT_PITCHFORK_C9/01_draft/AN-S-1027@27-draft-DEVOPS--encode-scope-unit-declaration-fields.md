---
atom_family: SPEC
atom_id: AN-S-1027
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: draft
  version: 27
  updated_at: 2026-11-05 12:58:42 +0400
---
## Summary

Encode Scope Unit declaration fields

## Claim

### Prose Claim


Carry a Scope Unit Declaration as a Markdown Atom. Its frontmatter carries Role = Requirement, Form = Scope Unit Declaration and the specific Scope Unit as `subjects.active`. Its Claim carries the declared structural facts in CFEL.

The shared Scope Unit model supplies field formats and cardinalities. Project inherits its unordered state and absence of order.number from the Project model. Folder names are derived by the shared Delivery Policy; they are not authored in a Declaration.
