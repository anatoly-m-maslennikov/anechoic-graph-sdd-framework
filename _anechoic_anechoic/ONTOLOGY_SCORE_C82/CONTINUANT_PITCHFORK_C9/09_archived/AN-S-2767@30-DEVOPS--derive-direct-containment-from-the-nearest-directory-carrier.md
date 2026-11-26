---
atom_family: SPEC
atom_id: AN-S-2767
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 30
  updated_at: "2026-11-25T17:50:12.199478+00:00"
---
## Summary

Derive Direct Containment from the Nearest Directory Carrier

## Claim

### Prose Claim

For an Atom whose `Header.Container` resolves to a Scope Unit or an Atom, derive the direct `IS_CONTAINED_BY` view from the nearest eligible Directory Carrier and its resolved container ID. The resolved ID must agree with the Atom’s declared `Header.Container`; its Carrier placement follows the corresponding Scope Unit or containing Atom folder. The derived view and its inverse `CONTAINS` represent the same declared containment fact, not a second authored fact.

## Details

Resolve `Header.Container` as a mapping with exactly one of `scope_unit` or `atom`; the Scope Unit reference uses its stable ID. Apply the admitted reference and placement rules. If placement and the declared Container disagree, report the disagreement without replacing the declared logical parent from a directory. Reading or refreshing the inverse view does not edit the containing Object’s Carrier or create a new Atom Version. Project Structure remains authoritative for declared Scope Unit parentage under CA-R-1660.
