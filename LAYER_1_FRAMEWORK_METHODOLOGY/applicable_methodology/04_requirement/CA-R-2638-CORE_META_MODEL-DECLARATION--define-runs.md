---
atom_id: CA-R-2638
ref_id: CA-R-2638
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Relation//RUNS
tier: 3
status: active
version: 4
updated_at: 2026-11-05 02:06:39 +0400
carrier_destination:
  file:
    name: CA-R-2638-CORE_META_MODEL-DECLARATION--define-runs.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2638-CORE_META_MODEL-DECLARATION--define-runs.md
  source_atom_id: CA-R-2638
  source_atom_revision: 4
  source_sha256: 67778394090b933cdaff431e50e7faaa28d73e9d5f0e8b5a696ffc13a8632e1d
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define RUNS

## Claim

### Prose Claim

RUNS binds a Step invocation to its Action or Workflow. Its inverse is IS_RUN_BY.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='RUNS',
    inverse_alias='IS_RUN_BY',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role:=Operations)/Step',)},
    target_endpoint={
        'level': 'instances',
        'entity_paths': ('Atom/(.Header.Context.Role:=Operations)/Action', 'Atom/(.Header.Context.Role:=Operations)/Workflow'),
    },
)
```

