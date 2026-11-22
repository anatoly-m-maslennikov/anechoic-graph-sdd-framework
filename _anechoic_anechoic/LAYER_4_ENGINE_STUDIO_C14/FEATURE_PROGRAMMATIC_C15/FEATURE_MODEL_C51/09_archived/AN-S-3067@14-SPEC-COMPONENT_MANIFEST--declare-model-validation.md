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
  version: 14
  updated_at: "2026-11-22T03:44:51.739238+00:00"
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
                    'project_manifest__pub.manifest_state_fields',
                    'cardinality__pub.cardinality_bounds',
                    'model_class_subject__pub.canonical_model_address',
                    'property_order__pub.bind_ordering_declarations',
                    'property_order__pub.order_properties',
                    'code_access_rules__pub.module_visibility',
                    'code_access_rules__pub.parse_code_access',
                    'native_model_claim__pub.parse_native_model_claim',
                    'model_class_subject__pub.model_class_target',
                    'native_carrier_header__pub.native_header_view',
                    'atom_reference__pub.derive_atom_ref',
                ],
                'exports': {
                    'model_generation__pub.open_admitted_model': {'private': ['C50', 'C62']},
                    'model_generation__pub.verify_model': {'private': ['C50', 'C62']},
                    'FEATURE_MODEL_VALIDATION__shared': None,
                    'FEATURE_MODEL_VALIDATION__shared.bind_model_declarations': None,
                    'FEATURE_MODEL_VALIDATION__shared.bind_reviewed_instance_check': None,
                    'FEATURE_MODEL_VALIDATION__shared.check_code_access': {'shared': ['C45']},
                    'FEATURE_MODEL_VALIDATION__shared.effective_relation_constraints': None,
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
