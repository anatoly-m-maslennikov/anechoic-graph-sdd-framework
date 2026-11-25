---
atom_family: SPEC
atom_id: AN-S-2162
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 10
  updated_at: "2026-11-25T21:02:02.235806+00:00"
---

## Summary

Declare Event Record

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Recorded//Event Record

## Semantics

An Event Record retains information about an occurrence. Its Carrier represents the record. The recorded Event identifies the occurrence.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Recorded

class EventRecord(Recorded):
    node.classifications = {'Temporal Kind': 'Continuant'}
```
