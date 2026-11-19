---
atom_id: CA-R-2509
ref_id: CA-R-2509
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Concern)
tier: 3
status: active
version: 5
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-2509-CORE_META_MODEL-DECLARATION--declare-atom-role-concern.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2509-CORE_META_MODEL-DECLARATION--declare-atom-role-concern.md
  source_atom_id: CA-R-2509
  source_atom_revision: 5
  source_sha256: 105b7be6f75ae47902a48eeb4650792d77ff3840645a2354597627621177ca43
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Atom/(.Role := Concern)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom

class Concern(Atom):
    pass

declare_entity(entity_class=Concern, entity_name='Concern', qualification_property_path="Atom.Header.Context.Role", classifications={"Role Order Number": 1})
```

## Semantics

A Concern identifies a question, conflict, or problem.
