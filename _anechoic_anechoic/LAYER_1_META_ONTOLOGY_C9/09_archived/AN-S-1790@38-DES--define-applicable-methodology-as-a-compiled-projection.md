---
atom_family: SPEC
atom_id: AN-S-1790
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 38
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Define Applicable Methodology as a Compiled Projection

## Claim scope

Compilation of Applicable Methodology from selected Methodology Source Scope Units.

## Claim

Member identifies a projected Atom member by its source identity and Version; these references identify the members without changing their content or making the Projection authoritative. Each projected member retains the exact source relation required by CA-R-1314.

the Applicable Methodology **must** be a non-authoritative Reconciled Projection compiled by direct, content-preserving derivation from current active Atom Revisions **in** selected Methodology Source Scope Units, preserving the selected source Atoms **and** their final selected Revisions unchanged. Applicable Methodology is **not** a Scope Unit **and** **must not** be the Claim Target Scope Unit of a Goal Atom.

direct **and** content-preserving describe this derivation, **not** a Carrier persistence strategy; its Reconciled Projection classification does **not** select such a strategy. trace metadata **may** be added **to** projected Carriers **only** as governed by applicable Delivery authority, **without** changing the source Atom Revision **or** its Claim authority.

### Formal claim

```text
Entity/Object/Continuant/Projection/Type: Applicable Methodology.Member[string]{0+}
```
