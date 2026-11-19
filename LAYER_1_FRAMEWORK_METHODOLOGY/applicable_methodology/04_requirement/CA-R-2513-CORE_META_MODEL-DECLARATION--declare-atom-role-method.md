---
atom_id: CA-R-2513
ref_id: CA-R-2513
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Method)
tier: 3
status: active
version: 7
updated_at: '2026-11-12T12:33:04.158402+00:00'
carrier_destination:
  file:
    name: CA-R-2513-CORE_META_MODEL-DECLARATION--declare-atom-role-method.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2513-CORE_META_MODEL-DECLARATION--declare-atom-role-method.md
  source_atom_id: CA-R-2513
  source_atom_revision: 7
  source_sha256: 697fecfcade629667889493a5fd5be205fcb0e2ccfafcfaa106cd6682069b1b1
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Atom/(.Role := Method)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom

class Method(Atom):
    pass

declare_entity(
    entity_class=Method,
    entity_name='Method',
    qualification_property_path='Atom.Header.Context.Role',
    classifications={'Role Order Number': 5},
)
```

## Semantics

A Method specifies domain and engineering designs, mechanisms or working approaches for achieving required results.
