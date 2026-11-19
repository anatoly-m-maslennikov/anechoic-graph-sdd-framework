---
atom_id: CA-R-2200
ref_id: CA-R-2200
container:
  scope_unit: CA-SU-13
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Carrier/Git Branch
tier: 1
status: active
version: 8
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-2200-PROJECT_CONFIGURATION-DECLARATION--define-git-branch-carrier.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement/CA-R-2200-PROJECT_CONFIGURATION-DECLARATION--define-git-branch-carrier.md
  source_atom_id: CA-R-2200
  source_atom_revision: 8
  source_sha256: fe02416934e5b860869bd9902d0e559f8335460a4aeeb5fa7fd08af63c85cfd6
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define Git Branch Carrier

## Claim

### Prose Claim

A Git Branch is a repository-owned Carrier identifying a branch head.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Carrier

class GitBranch(Carrier):
    pass

declare_entity(entity_class=GitBranch, entity_name='Git Branch')
```

## Semantics

A Git Repository contains its Git Branches; this is containment, not specialization.
