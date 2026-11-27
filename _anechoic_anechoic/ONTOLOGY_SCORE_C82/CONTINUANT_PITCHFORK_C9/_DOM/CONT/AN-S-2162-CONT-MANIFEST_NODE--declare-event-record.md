---
atom_family: SPEC
atom_id: AN-S-2162
concern:
  subject: Event Record
  path: Model/Graph/Node//Artifact//SSOT//Recorded
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 15
  updated_at: '2026-11-26T18:38:58.296902+00:00'
---

## Summary

Declare Event Record

## Semantics

An Event Record retains information about an occurrence. Its authoritative Carrier is the stored Journal record in the database. The recorded Event identifies the occurrence. A Journal observation can supply partial evidence about an Event Record. Preserve the time facts that the evidence supports. An Event Record reports the occurrence and its observed outcome. A separate evaluation can judge the outcome against an applicable Spec.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import DatabaseRecord, Recorded

class EventRecord(Recorded):
    node.axes = {'Temporality': 'Continuant'}
    node.ssot_carrier = value(fixed=DatabaseRecord)
```
