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
  version: 8
  updated_at: '2026-11-24T16:58:01.303567+00:00'
---

## Summary

Declare Event Record

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Recorded//Event Record

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Recorded

class EventRecord(Recorded):
    classifications = {'Temporal Kind': 'Continuant'}
```
