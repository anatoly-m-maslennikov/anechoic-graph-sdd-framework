---
atom_family: SPEC
atom_id: AN-S-3067
container:
  component: C51
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 9
  updated_at: "2026-11-22T03:03:47.718844+00:00"
---

## Summary

Declare MODEL_VALIDATION

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C53',
        name='MODEL_VALIDATION',
        lens_whitelist=['DES'],
        boundaries={
            'code': {
                'imports': [
                    'model_class_subject__pub.model_class_target',
                    'native_carrier_header__pub.native_header_view',
                    'atom_reference__pub.derive_atom_ref',
                ],
                'exports': {
                    'FEATURE_MODEL_VALIDATION__shared': None,
                    'FEATURE_MODEL_VALIDATION__shared.bind_model_declarations': None,
                    'FEATURE_MODEL_VALIDATION__shared.bind_ordering_declarations': None,
                    'FEATURE_MODEL_VALIDATION__shared.bind_reviewed_instance_check': None,
                    'FEATURE_MODEL_VALIDATION__shared.build_code_access_ownership': {'shared': ['C16', 'C45']},
                    'FEATURE_MODEL_VALIDATION__shared.check_code_access': {'shared': ['C16', 'C45']},
                    'FEATURE_MODEL_VALIDATION__shared.effective_relation_constraints': None,
                    'FEATURE_MODEL_VALIDATION__shared.order_properties': None,
                    'FEATURE_MODEL_VALIDATION__shared.validate_relation_endpoint_levels': None,
                    'FEATURE_MODEL_VALIDATION__shared.validate_relation_targets': None,
                    'FEATURE_MODEL_VALIDATION__pub': 'public',
                    'FEATURE_MODEL_VALIDATION__pub.validate_model_instance': 'public',
                    'FEATURE_MODEL_VALIDATION__pub.BoundNativeModel': 'public',
                    'FEATURE_MODEL_VALIDATION__shared.normalize_reviewed_claim': None,
                    'FEATURE_MODEL_VALIDATION__shared.reviewed_claim_sha256': None,
                },
            },
        },
    ),
)
```
