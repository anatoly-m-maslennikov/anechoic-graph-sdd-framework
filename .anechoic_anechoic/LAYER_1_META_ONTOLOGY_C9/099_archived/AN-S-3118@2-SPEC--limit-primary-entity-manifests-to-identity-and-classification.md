---
identity:
  atom_id: AN-S-3118
context:
  container:
    component: C9
  lens: SPEC
state:
  status: archived
  version: 2
  updated_at: '2026-11-20T16:02:18.721582+00:00'
---

## Summary

Limit Primary Entity Manifests to identity and classification

## Claim

### Prose Claim

A Primary Entity Manifest may contain only the Entity name, the class symbol
and its bases, Primary classification, and the optional identity rule.
The identity rule names the Properties that identify an instance. The class
body has no fields. The class bases declare inheritance.

Declare each Property in its own Manifest. A Property uses `IS_PROPERTY_OF`
to name its explicit bearer and declares its value type and cardinality.
The Claim scope matches the Property name and its bearer or subtype target.
Property paths in identity and derivation rules are relative to the nearest
Primary Entity. Nested Properties resolve through their declared bearers.
A subtype inherits each applicable Property. It can tighten or loosen the
original Property by declaring a constraint scoped to the subtype. Model
constraints name their owning Entity in a separate declaration.

Atom owns the Identity and State groups. Identity owns Atom ID. State owns
Version, Status, and Updated At. Identity stays in the Atom Header, including
its `identity.atom_id` field. Atom ID identifies the Atom across revisions.
Ref ID is a separate derived Property. Model objects compute it on read
from Atom ID and State.Version. It adds `-draft` if State.Status is Draft.
An Active revision keeps its exact Ref ID when it is Archived. Atom
Carriers store only the input Properties.

## References

AN-T-2923, AN-T-2924, AN-S-149.
