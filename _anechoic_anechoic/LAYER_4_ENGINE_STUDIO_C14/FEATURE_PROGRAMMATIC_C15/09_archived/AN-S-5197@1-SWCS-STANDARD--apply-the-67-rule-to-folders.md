---
atom_family: SPEC
atom_id: AN-S-5197
concern:
  subject: Folder
  path: Model/Carrier/Filesystem
  relation: is_contained_by
container:
  component: C15
tier: 0
context:
  template: STANDARD
  lens: SWD/SWCS
state:
  status: archived
  version: 1
  updated_at: "2026-11-28T12:41:05+00:00"
---

## Summary

Apply the 67 Rule to folders

## Semantics

### Folder budget

Budget 42 KiB (43,008 bytes) for the files a folder owns directly. This is
seven 6 KiB module budgets. Count all regular files in the Static
inventory at their stored byte size, including assets and fixtures.
Check each child folder on its own.

Count up to five direct subfolders and one additional test subfolder.
A test subfolder has a name ending in `__tests`. Derive folders from
tracked and nonignored files after excluding generated runtime state.

## Claim

### Formal Claim

```lean
namespace SourceFolderBounds

def conforms (directBytes subfolders testSubfolders : Nat) : Bool :=
  decide (directBytes ≤ 42 * 1024 ∧ subfolders ≤ 5 ∧ testSubfolders ≤ 1)

end SourceFolderBounds
```
