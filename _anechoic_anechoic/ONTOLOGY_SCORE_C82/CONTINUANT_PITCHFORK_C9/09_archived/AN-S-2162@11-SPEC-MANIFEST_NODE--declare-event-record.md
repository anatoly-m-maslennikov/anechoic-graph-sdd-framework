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
  version: 11
  updated_at: "2026-11-25T22:54:35.574289+00:00"
---

## Summary

Declare Event Record

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Recorded//Event Record

## Semantics

An Event Record retains information about an occurrence. Its Carrier represents the record. The recorded Event identifies the occurrence. A Journal observation can supply partial evidence about an Event Record. Preserve the time facts that the evidence supports.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Recorded

class EventRecord(Recorded):
    node.classifications = {'Temporal Kind': 'Continuant'}
```
