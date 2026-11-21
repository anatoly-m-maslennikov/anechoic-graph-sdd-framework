---
atom_family: SPEC
atom_id: AN-S-1613
structure:
  container:
    component: C00
  tier: 1
context:
  lens: DES
state:
  status: draft
  version: 21
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Separate check mechanism labels from Evaluation Atom Types

## Claim scope

mechanism labels and admitted Type values for Evaluation Atoms.

## Claim

the mechanism labels `Test` **and** `Evaluation` **must** describe implementation mechanisms, **not** Type values under `Atom/Content Role: Evaluation/Type`. the governing Evaluation Atom **and** its realization **must not** acquire the same classification merely because their names overlap.

## Details

this distinction does **not** define another Content Role **or** close the admitted Evaluation Type domain. its separately governed Type values remain subject **to** the applicable Type authority.
