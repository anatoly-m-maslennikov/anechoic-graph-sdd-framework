---
atom_family: SPEC
atom_id: AN-S-2883
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-10-29 09:06:21 +0400
---
## Summary

Define Project

## Claim scope

The Project as a whole in the primary Subject structure.

## Claim

Project means the whole project as one entity, distinct from any particular part such as an Atom or Implementation.

### Formal claim

```text
Scope Unit/Project.Parent{0}
```

## Semantics

This Subject addresses claims about the project as a whole. Atoms, Implementation, governing configurations and other project parts retain their own Subjects.

Project Model groups the vocabulary for Project and its parts. Project is the whole entity addressed by a Subject; Project Model is the vocabulary grouping.

The root Scope Unit organizes the project's Atoms and child Scope Units. Implementation and the repository Carrier are distinct project parts or representations; none replaces the whole-project Subject.
