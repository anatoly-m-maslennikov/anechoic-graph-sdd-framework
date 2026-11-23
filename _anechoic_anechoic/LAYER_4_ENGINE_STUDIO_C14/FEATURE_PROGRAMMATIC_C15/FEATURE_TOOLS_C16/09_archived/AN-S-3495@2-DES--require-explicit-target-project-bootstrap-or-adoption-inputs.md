---
atom_family: SPEC
atom_id: AN-S-3495
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-10-14 20:53:35 +0400
---
## Summary

Require explicit target-Project bootstrap or adoption inputs

# Summary

Require explicit target-Project bootstrap or adoption inputs

## Scope

the input boundary that identifies an installation target.

## Claim

the INSTALL_TOOLS facade **must** receive explicit target root, control child, bootstrap-or-adopt mode, settings, Project Structure and registry, and **must not** invent an Operator or missing target input.

## Details

Bootstrap admits a declared Project with an empty runtime boundary; adoption admits pre-existing Project metadata but still requires an empty active runtime boundary for CA-R-1881. Every input is reopened and digested into CA-D-600 before state is written. Ambiguous roots, absent controls, changed settings or inferred Operator identity refuse without effects.
