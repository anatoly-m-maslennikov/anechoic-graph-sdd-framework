---
identity:
  atom_id: CA-R-3177
  ref_id: CA-R-3177@1-draft
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: requirement
  topics:
    main_subject: MODEL//ANECHOIC <+ Atom
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:04:39.794555+00:00'
destination:
  file:
    name: CA-R-3177@1-draft-CORE_META_MODEL-REQUIREMENT--define-direct-relations-and-their-inverse-endpoints.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Define direct Relations and their inverse endpoints

## Claim

### Prose Claim

A Relation is named and directed; each direct fact connects its source and target. Persist a direct fact once. Each explicit Atom-to-Atom Relation has a derived reverse endpoint for the same direct pair. An inverse endpoint does not independently assert a second fact. Component child_of and children are direct inverses. Transitive results are derived in Views and do not expand a direct inverse endpoint.

## Details

During mechanical migration, carry forward verified legacy declarations
and authored direct relations with remapped endpoints. Keep
`TIER_CHILD_OF` for legacy Atom-tier links and `CHILD_OF` for
Components. Hold unresolved declarations or endpoints.

Acceptance: if Standard S contributes_to Solution A and A contributes_to Solution B, B's direct reverse endpoint includes A, not S. A View may report S as a transitive contributor to B. A direct inverse of S contributes_to A reverses precisely that pair.

Sources: CA-A-1462@1-draft, CA-R-2247@16. Task: CA-P-3080.
