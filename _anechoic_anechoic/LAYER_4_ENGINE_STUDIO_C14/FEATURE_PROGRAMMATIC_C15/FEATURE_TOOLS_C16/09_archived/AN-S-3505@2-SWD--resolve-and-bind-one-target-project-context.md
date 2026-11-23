---
atom_family: SPEC
atom_id: AN-S-3505
container:
  component: C16
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 2
  updated_at: 2026-10-14 20:53:35 +0400
---
## Summary

Resolve and bind one target-Project context

# Summary

Resolve and bind one target-Project context

## Scope

the bootstrap, adoption and relocation resolution procedure for one target Project.

## Claim

the INSTALL_TOOLS facade **must** resolve and digest exactly supplied target controls **before** state staging, and **must not** infer missing Project identity or Operator intent.

## Details

1. Read supplied target root, control child, mode, settings, Structure and registry; distinguish non-git, sibling-project and relocation topology.
2. Reopen and digest all controls into CA-D-600; link relocation to its predecessor only after identity revalidation.
3. For first activation, verify the runtime selector, runtime state and public Skill boundary are empty; adoption permits metadata only.
4. Acquire the target lock after successful context binding. Changed, ambiguous or existing-active-runtime inputs refuse without effects.
