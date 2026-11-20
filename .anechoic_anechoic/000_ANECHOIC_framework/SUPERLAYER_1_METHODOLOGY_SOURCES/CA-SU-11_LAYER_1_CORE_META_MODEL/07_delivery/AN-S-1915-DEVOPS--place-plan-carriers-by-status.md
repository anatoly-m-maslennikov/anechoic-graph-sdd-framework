---
identity:
  atom_id: AN-S-1915
context:
  container:
    component: C9
  tier: 1
  lens: DevOps
state:
  status: active
  version: 33
  updated_at: '2026-11-11T19:06:04+04:00'
---
## Summary

Place Plan Carriers by Status

## Claim

### Prose Claim


Current Plan Carrier Bundle placement by carried Status.


Apply CA-D-466 for Current Plan placement.

Status folders are Carrier directories. Validate folder nesting against the child's direct `IS_CONTAINED_BY` declaration.

read Status from the Plan's own Markdown file under CA-D-483 **and** check its local placement; a parent **or** folder name **must not** supply a descendant's Status at read time. **every** admitted parent Status change requires the containment cascade under CA-R-1521: separate single-Atom Actions write the Status prescribed by CA-R-1521 to each selected latest descendant under its own model, without an optional descendant mode. For a containing Plan Atom whose requested Status is Done **or** Canceled, preserve every selected latest contained Plan already Done **or** Canceled and request Canceled for every other selected latest contained Plan. After the cascade, every selected latest contained Plan must be Done **or** Canceled; mixed terminal statuses are allowed, and no contained Plan is forced to match the parent's requested Status merely because the parent is Done **or** Canceled. For other admitted parent Statuses, preserve the applicable cascade. Archive selects the latest Atoms in the logical Container chain. Other references and older archived Revisions are excluded. Apply the Current layout to Current descendants. Apply CA-D-475 to Backlog descendants. Resolve descendants through logical Container, including Backlog Plans placed in the shared Backlog folder.

## Details

- Preserve exact older version bytes **without** rewriting their Version **or** Status. Retained-history subtrees and non-Atom assets may move byte-for-byte with an authorized matching Directory Carrier move; they are not independent Status targets. This does **not** authorize independent legacy-tree migration.
