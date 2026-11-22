---
atom_family: SPEC
atom_id: AN-S-1613
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: active
  version: 21
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Separate check mechanism labels from Evaluation Atom Types

## Claim

### Prose Claim


mechanism labels and admitted Type values for Evaluation Atoms.


the mechanism labels `Test` **and** `Evaluation` **must** describe implementation mechanisms, **not** Type values under `Atom/(.Header.Role := Evaluation).Header.Form`. the governing Evaluation Atom **and** its realization **must not** acquire the same classification merely because their names overlap.

## Details

this distinction does **not** define another Content Role **or** close the admitted Evaluation Type domain. its separately governed Type values remain subject **to** the applicable Type authority.
