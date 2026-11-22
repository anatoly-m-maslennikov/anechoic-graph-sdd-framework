---
atom_family: SPEC
atom_id: AN-S-371
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: active
  version: 31
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Requirement — Provide lineage-impact Projections

## Claim

### Prose Claim


lineage-impact Projections for changed, replaced, or archived Atom revisions.


ANECHOIC provides a non-authoritative lineage-impact Projection whenever an upstream Atom revision is changed, replaced, **or** archived. the Projection derives the reachable descendant set **without** modifying **or** retargeting **any** persisted relation.

for **every** affected descendant, the Projection identifies the exact earlier revision **in** its lineage, the upstream event that triggered review, **and** the current disposition: review required, update the existing Atom, create a new Atom, archive the Atom, **or** confirmed compatible **without** change. unresolved descendants remain visible **until** disposition is recorded through governed history.

the Projection **may** group **and** prioritize work, but it **must not** change an Atom, break a historical link, **or** establish compatibility merely by listing it.

## Primary claim

a changed, replaced, **or** archived ancestor produces a derived review surface for **every** affected descendant while historical lineage remains intact.
