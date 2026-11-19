---
atom_id: CA-R-2198
ref_id: CA-R-2198
container:
  scope_unit: CA-SU-13
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Carrier/Docker Image
tier: 1
status: active
version: 8
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-2198-PROJECT_CONFIGURATION-DECLARATION--define-docker-image-carrier.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement/CA-R-2198-PROJECT_CONFIGURATION-DECLARATION--define-docker-image-carrier.md
  source_atom_id: CA-R-2198
  source_atom_revision: 8
  source_sha256: 34bfee2caf8de6fbb0a47d32f542852d326a42dc5aba0abf45e6aa6721b58f5c
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define Docker Image Carrier

## Claim

### Prose Claim

A Docker Image is an immutable, addressable Carrier of packaged Implementation.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Carrier

class DockerImage(Carrier):
    pass

declare_entity(entity_class=DockerImage, entity_name='Docker Image')
```

