---
atom_family: SPEC
atom_id: AN-S-3008
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "draft"
  version: 1
  updated_at: '2026-11-25T12:58:58.877839+00:00'

---
## Summary

Validate lens narrowing and sibling overlap

## Claim

### Prose Claim

Expand each selected scope to canonical Lens paths. Accept each pair
when its sets are disjoint or one contains the other. Reject partial overlap.
Each owned Spec Atom uses one authored Lens path.

Declare group names and their member lists in
`ProjectManifest.parameters.project.lens_groups`. Members can be Lens paths
or other groups. Reject cycles. Match path segments with authored casing.
A selected Lens path covers its descendants.

## Details

Accept SWE with SWD in one Component. Reject SYS with BACKEND in one
Component because both include SWE and each has paths the other omits.
Accept SYS and BACKEND in different Components.

Sources: CA-A-1462@1-draft, CA-P-3081@1. Task: CA-P-3081.
