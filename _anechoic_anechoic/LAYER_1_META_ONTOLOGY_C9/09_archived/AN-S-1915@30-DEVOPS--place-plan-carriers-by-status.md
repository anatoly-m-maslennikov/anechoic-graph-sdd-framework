---
atom_family: SPEC
atom_id: AN-S-1915
container:
  component: C9
tier: 1
context:
  lens: DevOps
state:
  status: archived
  version: 30
  updated_at: '2026-11-11T17:45:31+04:00'
---
## Summary

Place Plan Carriers by Status

## Claim

### Prose Claim


Current Plan Carrier Bundle placement by carried Status.


Use these Status mappings relative to the Current placement base:

- Active uses the base directory.
- Backlog: **in** its `001_backlog` subdirectory.
- Done: **in** its `done` subdirectory.
- Canceled: **in** its `canceled` subdirectory.

Status folders are Carrier directories. Validate folder nesting against the child's direct `IS_CONTAINED_BY` declaration.

read Status from the Plan's own Markdown file under CA-D-483 **and** check its local placement; a parent **or** folder name **must not** supply a descendant's Status at read time. **every** admitted parent Status change requires the containment cascade under CA-R-1521: separate single-Atom Actions write the Status prescribed by CA-R-1521 to each selected latest descendant under its own model, without an optional descendant mode. For a containing Plan Atom whose requested Status is Done **or** Canceled, preserve every selected latest contained Plan already Done **or** Canceled and request Canceled for every other selected latest contained Plan. After the cascade, every selected latest contained Plan must be Done **or** Canceled; mixed terminal statuses are allowed, and no contained Plan is forced to match the parent's requested Status merely because the parent is Done **or** Canceled. For other admitted parent Statuses, preserve the applicable cascade. Archive selects all contained latest Atoms; references outside the Carrier tree **and** older archived Revisions are excluded. retain Current descendants inside the parent Carrier tree.

## Details

- Preserve exact older version bytes **without** rewriting their Version **or** Status. Retained-history subtrees and non-Atom assets may move byte-for-byte with an authorized matching Directory Carrier move; they are not independent Status targets. This does **not** authorize independent legacy-tree migration.
