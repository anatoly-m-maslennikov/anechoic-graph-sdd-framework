---
atom_family: SPEC
atom_id: AN-S-4854
concern:
  subject: HAS_REALIZATION
  path: Model/Graph/Relation
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_relation
  lens: DOM/CONT
state:
  status: "active"
  version: 4
  updated_at: "2026-11-26T16:34:52.407547+00:00"
---

## Summary

Declare HAS_REALIZATION

## Claim

### Prose Claim

An Atom has a realization in a Package or Module. The Package's
`{package}__spec_bind.yaml` sidecar carries the binding. This declaration
does not create an independent binding or infer Module edges from a Package
binding. Existing Artifact, Ticket, and binding rules remain authoritative.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Module, Package, Relation

class Relation4854(Relation):
    name = 'HAS_REALIZATION'
    relation.inverse_alias = 'IS_REALIZATION_OF'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Atom,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Package, Module)}
```
