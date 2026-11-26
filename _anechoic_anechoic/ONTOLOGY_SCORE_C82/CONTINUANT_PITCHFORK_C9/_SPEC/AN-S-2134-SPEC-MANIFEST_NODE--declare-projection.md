---
atom_family: SPEC
atom_id: AN-S-2134
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 7
  updated_at: "2026-11-25T22:50:26.516034+00:00"
---

## Summary

Declare Projection

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//Derived//Projection

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Derived

class Projection(Derived):
    pass
```

## Semantics

A Projection derives a view from source entities. Building, refreshing, or removing the view preserves the identity and authority of those entities. The derivation defines the view independently of its storage. The Projection specification identifies the derivation and configuration for a rebuild. Persist dependency provenance where the Projection specification or its registered job requires it. Preserve the applicable source traceability. Keep source identity and Relation direction when combining Projections. Retain the source coverage of each input and distinguish external references from selected graph members.
