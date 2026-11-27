---
atom_family: SPEC
atom_id: AN-S-2691
concern:
  subject: CARRIES_SSOT_FOR
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
  version: 22
  updated_at: "2026-11-26T14:46:18.747397+00:00"
---
## Summary

Declare CARRIES_SSOT_FOR

## Semantics

The Carrier holds the authoritative representation of the Artifact. Use the Carrier location declared for the Artifact kind. For an Atom, bind the file to the exact revision identified by its Header.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Asset, AtomFamily, Carrier, Component, EventRecord, Module, Package, Prompt, Relation, Unit

class CarriesSSOTFor(Relation):
    name = 'CARRIES_SSOT_FOR'
    relation.inverse_alias = 'HAS_SSOT_CARRIER'
    relation.endpoint_pairs = (
        {
            'source_endpoint': {'level': 'instances', 'entity_paths': (Carrier,)},
            'target_endpoint': {
                'level': 'instances',
                'entity_paths': (Atom,),
                'reference_form': 'exact_atom_revision',
            },
        },
        {
            'source_endpoint': {'level': 'instances', 'entity_paths': (Carrier,)},
            'target_endpoint': {
                'level': 'instances',
                'entity_paths': (Asset, AtomFamily, Component, EventRecord, Module, Package, Prompt, Unit),
            },
        },
    )
    relation.sources_per_target = 1
```
