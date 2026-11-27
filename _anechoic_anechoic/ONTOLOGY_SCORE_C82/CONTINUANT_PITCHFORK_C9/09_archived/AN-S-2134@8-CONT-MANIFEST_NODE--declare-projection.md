---
atom_family: SPEC
atom_id: AN-S-2134
concern:
  subject: Projection
  path: Model/Graph/Node//Artifact//Derived
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 8
  updated_at: "2026-11-26T17:13:48.988587+00:00"
---

## Summary

Declare Projection

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Derived

class Projection(Derived):
    pass
```

## Semantics

A Projection builds a view from source Carrier content. Building, refreshing, or removing the view preserves the identity and authority of those entities. The derivation defines the view independently of its storage. The Projection specification identifies the derivation and configuration for a rebuild. When the Projection specification or its registered job requires provenance, record each exact input through `IS_DERIVED_FROM`. Preserve the applicable source traceability. Keep source identity and Relation direction when combining Projections. Retain the source coverage of each input and distinguish external references from selected graph members.
