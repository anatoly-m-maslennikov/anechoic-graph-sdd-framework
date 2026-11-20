---
atom_family: SPEC
atom_id: AN-S-3036
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:04:39.794555+00:00'
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
