---
atom_family: SPEC
atom_id: AN-S-4442
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 05:13:56 +0400
---

## Summary

Declare CFEL containment operator /

## Claim

### Prose Claim

`Whole/Part` expresses the immediate `CONTAINS` Relation from Whole to Part. Its corresponding direct `IS_CONTAINED_BY` fact runs from Part to Whole. Containment does not imply narrowing or inheritance.

When directional cardinality slots are present, the slot before `/` counts outgoing `CONTAINS` links per Whole, and the slot after `/` counts reverse `IS_CONTAINED_BY` links per Part. Omitted slots remain unspecified. A Relation declaration or an applicable endpoint permission supplies its own bounds.

### Formal Claim

```CFEL
# model
Operator//Containment == "/"
```

## Semantics

`/` expresses immediate containment from a Whole to a Part.
