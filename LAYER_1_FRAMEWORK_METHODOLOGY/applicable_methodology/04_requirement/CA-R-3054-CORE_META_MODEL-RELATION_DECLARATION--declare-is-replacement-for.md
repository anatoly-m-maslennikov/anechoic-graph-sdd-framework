---
identity:
  ref_id: CA-R-3054
  id: CA-R-3054
context:
  container:
    scope_unit: CA-SU-11
  role: Requirement
  form: Relation Declaration
  topics:
    main_subject: ANECHOIC_MODEL <+ Relation//IS_REPLACEMENT_FOR
  tier: 4
relations:
  IS_REPLACEMENT_FOR:
  - CA-R-3011
state:
  status: active
  version: 2
  updated_at: '2026-11-12T12:33:04.158402+00:00'
destination:
  file:
    name: CA-R-3054-CORE_META_MODEL-RELATION_DECLARATION--declare-is-replacement-for.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
author: Anatoly Maslennikov
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3054-CORE_META_MODEL-RELATION_DECLARATION--declare-is-replacement-for.md
  source_atom_id: CA-R-3054
  source_atom_revision: 2
  source_sha256: 53321a210f9c49b09004f4794f6008751492d11d3d7ce4372096e0224294426e
  original_relations_sha256: fc0377d97037e13c78c1def4a49845e5df418a9be3bfe4194c09040ec2b1708f
---

## Summary

Declare IS_REPLACEMENT_FOR

## Claim

### Prose Claim

The Host is a replacement Atom. The Target is a predecessor Atom identified by its base Atom ID. One replacement can target several predecessors.

A Draft Host proposes replacement. Its links remain after promotion, including when the predecessor becomes Archived. Completed replacement requires an adopted successor and an Archived predecessor.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_REPLACEMENT_FOR',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',), 'reference_form': 'base_atom_id'},
)
```

## Semantics

IS_REPLACEMENT_FOR relates a replacement Atom to the predecessor Atom whose contribution it replaces.
