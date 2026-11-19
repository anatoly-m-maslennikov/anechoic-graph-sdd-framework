---
identity:
  id: CA-R-3052
  ref_id: CA-R-3052
context:
  container:
    scope_unit: CA-SU-11
  role: Requirement
  form: Declaration
  topics:
    main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations).Content.Operation
  tier: 4
state:
  status: active
  version: 3
  updated_at: '2026-11-12T18:59:51.161573+00:00'
destination:
  file:
    name: CA-R-3052-CORE_META_MODEL-DECLARATION--declare-legacy-operation-content.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
author: Anatoly Maslennikov
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3052-CORE_META_MODEL-DECLARATION--declare-legacy-operation-content.md
  source_atom_id: CA-R-3052
  source_atom_revision: 3
  source_sha256: 9fc3fe70cebb56189414feb65834d0d024842a69e480fe0ee9dabc6b8c9360eb
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare legacy Operation content

## Claim

### Prose Claim

An Operations Atom may retain its legacy Operation section during migration. Operation is a Markdown Content Property. Its presentation subheadings, lists and code blocks remain part of its value.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Operation',
    relation_name='IS_PROPERTY_OF',
    base_path='Atom.Content',
    applies_to_entity_classes=['Operations'],
    value_format='markdown',
    value_cardinality=Cardinality(minimum=0, maximum=1),
    dependent_property_cardinality=0,
)
```

## Semantics

Operation is the operation text carried by the legacy Operations Atom. This declaration describes that existing section; it does not decide whether a later Form must use Operation or Claim.
