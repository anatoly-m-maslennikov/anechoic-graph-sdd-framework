---
identity:
  atom_id: AN-S-386
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: 2026-11-04 05:21:15 +0400
---
## Summary

Bind direct Property values on instances

## Claim

### Prose Claim


HAS_VALUE binds a Property on an instance to its admitted literal value. For example, the version Property of Atom instance CA-P-123 has value 1. The Property declaration supplies its value format, admitted domain and cardinality; the literal 1 is not a separately declared graph Node and requires no Declaration Atom.

HAS_VALUE is a value binding rather than an ordinary Node-to-Node graph Relation. It must not create graph endpoints or independently authored inverse facts for literals. A Primary Node has no direct value. A Property instance may hold direct values where its effective declaration permits them, including inherited Property declarations. A Property occurrence on an instance is an instance of its effective declared Property and is borne by its data bearer. The declaration remains borne by its original model bearer. HAS_VALUE binds its admitted literal values and does not create an independent Carrier or graph endpoint for a value.
