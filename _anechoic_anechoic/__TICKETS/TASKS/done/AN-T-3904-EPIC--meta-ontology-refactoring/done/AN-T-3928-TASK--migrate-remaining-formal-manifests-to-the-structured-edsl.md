---
atom_family: TKT
atom_id: AN-T-3928
container:
  atom: AN-T-3904
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-25T16:01:56.595432+00:00"

---
## Summary

Migrate remaining Formal Manifests to the structured eDSL

## Work

After the class and eDSL update, migrate the other authoritative Formal Manifests, including the Project Custom Model. Use the same structure for constraints. Remove repeated Model scopes where the compiler can derive the address.

Review Semantics in every Formal Manifest. Explain what each declaration means. Remove prose that repeats constraints already expressed in the Formal Manifest.

## Acceptance

Compile the complete Model. Verify that migrated declarations preserve Model addresses and constraints except for approved semantic changes.

## Verification

Published 116 style revisions and removed 39 redundant Claim scopes. Reviewed Semantics and removed repeated prose from nine Manifests. All 190 Model declarations compiled. Atom Relations was the only formal rule change.
