---
atom_id: CA-R-2965
ref_id: CA-R-2965
container:
  scope_unit: CA-SU-11
role: Requirement
form: Relation Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Relation//IS_ORDERED_RIGHT_AFTER
tier: 3
status: active
version: 4
updated_at: '2026-11-14T07:33:24.792510+00:00'
carrier_destination:
  file:
    name: CA-R-2965-CORE_META_MODEL-RELATION_DECLARATION--declare-is-ordered-right-after.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2965-CORE_META_MODEL-RELATION_DECLARATION--declare-is-ordered-right-after.md
  source_atom_id: CA-R-2965
  source_atom_revision: 4
  source_sha256: b75f197da963899385ff4d3794bb075d1fb5799f72024d9b3ee20953c6807d13
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare IS_ORDERED_RIGHT_AFTER

## Claim

### Prose Claim

IS_ORDERED_RIGHT_AFTER relates Atom Header or Content Property instances. The Host immediately follows the Target in sibling order. The inverse alias IS_ORDERED_RIGHT_BEFORE reads the same link in reverse.

`x ;> y` means x is immediately before y, in the order x; y. `x <; y` means x is immediately after y, in the order y; x.


### Formal Claim

```python
from caprmedio.formal_claims import declare_relation

declare_relation(
    relation_name='IS_ORDERED_RIGHT_AFTER',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom.Header.**', 'Atom.Content.**')},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom.Header.**', 'Atom.Content.**')},
    inverse_alias='IS_ORDERED_RIGHT_BEFORE',
    written_alias='<;',
    reverse_written_alias=';>',
)
```

## Semantics

IS_ORDERED_RIGHT_AFTER relates a Property instance to its immediately preceding sibling.
