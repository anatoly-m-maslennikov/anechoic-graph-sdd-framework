---
atom_family: SPEC
atom_id: AN-S-3628
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 14
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Classify each Realization Graph relation by derivation

# Summary

Classify each Realization Graph relation by derivation

## Scope

Represented Realization Graph Relations and their supported Relation Derivation Classes.

## Claim

**every** represented Realization Graph Relation **must** carry **`>=1`** supported Relation Derivation Classes, with the supporting source **or** execution evidence identified separately for **every** assigned class.

- **when** the same Relation is source-declared, resolved, **or** observed, multiple classifications **may** coexist; they describe evidence origins, **not** mutually exclusive truth values.
- a class identifies how the Relation was obtained. it does **not** prove that the Relation is required, correct, exhaustive, **or** currently applicable.
- missing **or** conflicting derivation evidence remains an explicit unresolved diagnostic; an unsupported class **or** Relation **must not** be presented as established.

## Details

