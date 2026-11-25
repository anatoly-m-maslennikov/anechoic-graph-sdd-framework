---
atom_family: SPEC
atom_id: AN-S-371
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 26
  updated_at: 2026-10-27 20:00:01 +0400
---
## Summary

Requirement — Provide lineage-impact Projections

# Summary

Requirement — Provide lineage-impact Projections

## Scope

lineage-impact Projections for changed, replaced, or archived Atom revisions.

## Claim

ANECHOIC provides a non-authoritative lineage-impact Projection whenever an upstream Atom revision is changed, replaced, **or** archived. the Projection derives the reachable descendant set **without** modifying **or** retargeting **any** persisted relation.

for **every** affected descendant, the Projection identifies the exact earlier revision **in** its lineage, the upstream event that triggered review, **and** the current disposition: review required, update the existing Atom, create a new Atom, archive the Atom, **or** confirmed compatible **without** change. unresolved descendants remain visible **until** disposition is recorded through governed history.

the Projection **may** group **and** prioritize work, but it **must not** change an Atom, break a historical link, **or** establish compatibility merely by listing it.

## Primary claim

a changed, replaced, **or** archived ancestor produces a derived review surface for **every** affected descendant while historical lineage remains intact.

## Details
