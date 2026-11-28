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
  status: active
  version: 3
  updated_at: "2026-11-28T13:35:01+00:00"
---

## Summary

Apply the 67 Rule to folders

## Semantics

### Folder budget

Budget 42 KiB (43,008 bytes) for executable files directly in each folder.
Measure the stored bytes of files that the Realization Graph classifier
identifies as executable. Count up to seven direct non-executable files,
including assets, fixtures, and configuration.

Check each child folder on its own. The folder limits also apply to
folders that hold only assets or fixtures.

Count up to five ordinary direct subfolders and one direct test subfolder.
Use Project Structure to identify declared child Component folders.
Exclude those folders from the ordinary count and check their contents
under the same rule. A test subfolder name ends in `__tests`.
Derive folders from tracked and nonignored files after excluding
generated runtime state.

## Claim

### Formal Claim

```lean
namespace SourceFolderBounds

def conforms (executableBytes assets ordinarySubfolders testSubfolders : Nat) : Bool :=
  decide (executableBytes ≤ 42 * 1024 ∧ assets ≤ 7 ∧
    ordinarySubfolders ≤ 5 ∧ testSubfolders ≤ 1)

end SourceFolderBounds
```
