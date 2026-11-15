---
atom_id: CA-R-2475
ref_id: CA-R-2475
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Relation//NARROWER_THAN
tier: 3
status: active
version: 8
updated_at: '2026-11-13T22:36:02.766934+00:00'
carrier_destination:
  file:
    name: CA-R-2475-CORE_META_MODEL-DECLARATION--define-narrower-than.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2475-CORE_META_MODEL-DECLARATION--define-narrower-than.md
  source_atom_id: CA-R-2475
  source_atom_revision: 8
  source_sha256: fc899b1b6ca867f84f43e4d90c76e36d87b2675086893d2b65d3b479752269bb
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define NARROWER_THAN

## Claim

### Prose Claim

NARROWER_THAN relates a narrower MODEL kind to a broader MODEL kind. A Property does not narrow. Both endpoints are MODEL kinds; Property bearers and instance populations do not become kinds through this notation. The narrower kind inherits applicable Relation and Property constraints without cloning declarations or instance facts. HAS_NARROWER is its derived inverse. In `X/Y`, Y is narrower than X; traversal runs from broader to narrower.
### Formal Claim

```python
from caprmedio.formal_claims import declare_relation

declare_relation(
    relation_name='NARROWER_THAN',
    source_endpoint={'level': 'model_entities'},
    target_endpoint={'level': 'model_entities'},
    inverse_alias='HAS_NARROWER',
    reverse_written_alias='/',
)
```

