---
atom_family: SPEC
atom_id: AN-S-2668
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 24
  updated_at: 2026-10-27 19:59:54 +0400
---
## Summary

Keep one source for each relation fact

# Summary

Keep one source for each relation fact

## Scope

authoritative source declarations for Relation facts.

## Claim

**every** independently authored Relation fact **must** have **`=1`** authoritative source declaration under Single Source of Truth. its representation **in** multiple ANECHOIC Graph views remains a reference **or** derived Projection of that declaration **without** creating another independently maintained source.

a Relation derived under admitted derivation authority **must** remain traceable **to** that authority **and** its authoritative input facts, including through upstream Projections. it does **not** require a fabricated direct source declaration for the derived result. this distinction **must not** weaken a Relation Kind's requirement for an explicit source fact **or** permit unsupported inference.

## Details
