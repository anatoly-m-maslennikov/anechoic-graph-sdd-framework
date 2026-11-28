---
atom_family: SPEC
atom_id: AN-S-2715
concern:
  subject: IS_CONTAINED_BY
  path: Model/Graph/Relation
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_relation
  lens: DOM/CONT
state:
  status: archived
  version: 20
  updated_at: '2026-11-28T09:21:26.937336+00:00'
---

## Summary

Define composition and its inverse

## Axes

| Relation | Transitive | Functional |
| --- | --- | --- |
| `IS_CONTAINED_BY` | no | no |
| `CONTAINS` | no | no |

Both directions describe direct logical containment. AN-S-3147 gives each Atom one logical container. Recursive containment is defined in AN-S-2674.

An Atom Companion Container physically holds an Atom. This physical arrangement does not define logical containment.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import (
    Asset, Atom, AtomCompanionContainer, AtomFamily, Cardinality, Carrier,
    Axis, Component, ComponentPackage, Continuant, EDSL, EDSLClasses, EDSLFunctions,
    File, Folder, Format, Graph, Module, Node, Occurrent, Package, Prescribed,
    PrescribedContent, PrescribedStructure, Prompt, Realization, RealizationContent,
    RealizationStructure, Relation, Temporality, Unit,
    Lens, Model,
)

class Relation2715(Relation):
    name = 'IS_CONTAINED_BY'
    relation.endpoint_pairs = (
        {'source_endpoint': {'level': 'model_entities', 'entity_paths': (Graph, Carrier)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (Model,)}},
        {'source_endpoint': {'level': 'model_entities', 'entity_paths': (Node, Relation, EDSL, Axis, Lens)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (Graph,)}},
        {'source_endpoint': {'level': 'model_entities', 'entity_paths': (Folder, File)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (Carrier,)}},
        {'source_endpoint': {'level': 'model_entities', 'entity_paths': (Continuant, Occurrent)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (Temporality,)}},
        {'source_endpoint': {'level': 'model_entities', 'entity_paths': (PrescribedContent, PrescribedStructure)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (Prescribed,)}},
        {'source_endpoint': {'level': 'model_entities', 'entity_paths': (Atom,)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (PrescribedContent,)}},
        {'source_endpoint': {'level': 'model_entities', 'entity_paths': (AtomFamily, Component, AtomCompanionContainer)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (PrescribedStructure,)}},
        {'source_endpoint': {'level': 'model_entities', 'entity_paths': (RealizationContent, RealizationStructure)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (Realization,)}},
        {'source_endpoint': {'level': 'model_entities', 'entity_paths': (Module, Asset, Prompt)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (RealizationContent,)}},
        {'source_endpoint': {'level': 'model_entities', 'entity_paths': (Package,)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (RealizationStructure,)}},
        {'source_endpoint': {'level': 'model_entities', 'entity_paths': (Unit,)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (Module,)}},
        {'source_endpoint': {'level': 'model_entities', 'entity_paths': (EDSLClasses, EDSLFunctions)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (EDSL,)}},
        {'source_endpoint': {'level': 'model_entities', 'entity_paths': (Format, Cardinality)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (EDSLClasses,)}},
        {'source_endpoint': {'level': 'instances', 'entity_paths': (Atom,)}, 'target_endpoint': {'level': 'instances', 'entity_paths': (Component, Atom)}},
    )
    relation.acyclic = True
    relation.inverse_alias = 'CONTAINS'
    relation.reverse_written_alias = '<+'
```
