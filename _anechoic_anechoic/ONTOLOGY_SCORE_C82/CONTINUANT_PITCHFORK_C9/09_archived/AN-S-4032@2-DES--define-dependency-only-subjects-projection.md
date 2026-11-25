---
atom_family: SPEC
atom_id: AN-S-4032
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-10-29 07:17:21 +0400
---
## Summary

Define Dependency-only Subjects Projection

# Summary

Define Dependency-only Subjects Projection

## Claim

A Subject Graph Dependency-only Subjects Projection **means** the exact canonical Subject paths occurring in subjects.depends_on but not in subjects.governs within the same selected Current RMEDO source set. Apply the declared Subject-branch filter to those targets. List each path once with its referring Atom IDs, alphabetically. Governs references outside the selected sources do not remove a path from this view. Its entries describe selection-relative coverage, not proof of a project-wide missing definition.
