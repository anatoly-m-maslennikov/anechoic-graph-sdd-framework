---
atom_id: CA-R-2514
ref_id: CA-R-2514
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Evaluation)
tier: 3
status: active
version: 7
updated_at: '2026-11-12T12:33:04.158402+00:00'
carrier_destination:
  file:
    name: CA-R-2514-CORE_META_MODEL-DECLARATION--declare-atom-role-evaluation.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2514-CORE_META_MODEL-DECLARATION--declare-atom-role-evaluation.md
  source_atom_id: CA-R-2514
  source_atom_revision: 7
  source_sha256: 0d447da709858ca83524eb145ecbf58ebdcb84bedc7c56917e66f8480d579f22
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Atom/(.Role := Evaluation)

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import Atom

class Evaluation(Atom):
    pass

declare_entity(
    entity_class=Evaluation,
    entity_name='Evaluation',
    qualification_property_path='Atom.Header.Context.Role',
    classifications={'Role Order Number': 6},
)
```

## Semantics

An Evaluation specifies falsifiable checks and how their evidence is interpreted to determine whether required results are achieved.
