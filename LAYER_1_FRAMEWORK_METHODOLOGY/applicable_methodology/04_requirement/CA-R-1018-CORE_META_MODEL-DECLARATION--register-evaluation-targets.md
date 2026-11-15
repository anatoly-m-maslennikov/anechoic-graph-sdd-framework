---
atom_id: CA-R-1018
ref_id: CA-R-1018
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Relation//evaluation_for
  dependencies:
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Evaluation)
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Requirement)
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Method)
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Delivery)
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)
  - CAPRMEDIO_MODEL <+ Atom.Header.Context.Tier
tier: 1
status: active
version: 39
updated_at: '2026-11-12T12:33:04.158402+00:00'
carrier_destination:
  file:
    name: CA-R-1018-CORE_META_MODEL-DECLARATION--register-evaluation-targets.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1018-CORE_META_MODEL-DECLARATION--register-evaluation-targets.md
  source_atom_id: CA-R-1018
  source_atom_revision: 39
  source_sha256: 349db1d54cbe88654c5310e072eb70d2514c5d0aef72a90d46587ba16dfcf83b
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Register Evaluation targets

## Claim

### Prose Claim

#### Applicability
direct `evaluation_for` relations.

`evaluation_for` **means** the direct relation from an Evaluation Atom to an
Atom whose authority the Evaluation checks.

Forward `Host ((evaluation_for)) Target` and reverse `Target <((evaluation_for)) Host` are views of the same Relation fact.
evaluation_for relates Evaluation Atom to Atom whose authority is evaluated.
### Formal Claim

```python
from caprmedio.formal_claims import declare_relation

declare_relation(
    relation_name='evaluation_for',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role := Evaluation)',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
)
```

