---
atom_family: SPEC
atom_id: AN-S-3118
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-20T17:30:26.925863+00:00'
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

Atom ID belongs directly to the YAML Header. The Model path is
`Header.Atom ID`. State owns Status, Version, and Updated At. See
AN-S-3160 for the native Header order. Ref ID is computed from
Atom ID, Version, and Status. It adds `-draft` for a Draft.

## References

AN-T-2923, AN-T-2924, AN-S-149.
