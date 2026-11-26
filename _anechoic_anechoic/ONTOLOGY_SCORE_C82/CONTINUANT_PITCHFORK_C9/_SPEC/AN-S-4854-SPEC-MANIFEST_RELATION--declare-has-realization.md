---
atom_family: SPEC
atom_id: AN-S-4854
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T16:00:38.198754+00:00"
---

## Summary

Declare HAS_REALIZATION

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//HAS_REALIZATION

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
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Atom,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Package, Module)}
```
