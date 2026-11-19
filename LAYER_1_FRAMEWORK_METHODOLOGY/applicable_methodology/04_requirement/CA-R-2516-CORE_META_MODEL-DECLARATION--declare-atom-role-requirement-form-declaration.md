---
atom_id: CA-R-2516
ref_id: CA-R-2516
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Requirement)/(.Header.Context.Form
    := Declaration)
tier: 3
status: active
version: 7
updated_at: '2026-11-12T12:33:04.158402+00:00'
container:
  scope_unit: CA-SU-11
destination:
  file:
    name: CA-R-2516-CORE_META_MODEL-DECLARATION--declare-atom-role-requirement-form-declaration.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2516-CORE_META_MODEL-DECLARATION--declare-atom-role-requirement-form-declaration.md
  source_atom_id: CA-R-2516
  source_atom_revision: 7
  source_sha256: a24e73a6094405fcafc889d4189a5c9e0a74f26b1ced711f624d6fc05c103527
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Atom/(.Role := Requirement)/(.Form := Declaration)

## Claim

### Prose Claim


A Declaration states the applicable contract for its active Subject. Its Claim may contain several prose statements, Python formal expressions, or both when they form one coherent declaration about one topic.

Scope Unit Declaration is a Requirement Form using this template. It is not another Atom Role.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Requirement

class Declaration(Requirement):
    pass

declare_entity(
    entity_class=Declaration,
    entity_name='Declaration',
    qualification_property_path='Atom.Header.Context.Form',
)
```
