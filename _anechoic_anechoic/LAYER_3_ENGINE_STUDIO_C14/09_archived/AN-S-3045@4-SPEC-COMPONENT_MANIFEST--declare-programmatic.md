---
atom_family: SPEC
atom_id: AN-S-3045
container:
  component: C14
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-22T02:43:39.579096+00:00"
---

## Summary

Declare PROGRAMMATIC

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C15',
        name='PROGRAMMATIC',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
        boundaries={
            'code': {
                'imports': [
                    'carrier_read__pub.parse_carrier',
                    'carrier_compat__pub.carrier_read_view',
                    'carrier_compat__pub.matches_named_value',
                    'carrier_compat__pub.named_value_token',
                ],
                'exports': {
                    'FEATURE_PROGRAMMATIC__shared.Atom': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE']},
                    'FEATURE_PROGRAMMATIC__shared.DEPENDENCIES_CLAIM_SHA256': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE']},
                    'FEATURE_PROGRAMMATIC__shared.bindings_from_workbench_rows': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE']},
                    'FEATURE_PROGRAMMATIC__shared.dependencies_are_distinct': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE']},
                    'FEATURE_PROGRAMMATIC__shared.emits_instance_inverse': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH']},
                    'FEATURE_PROGRAMMATIC__shared.has_dataclass_field_contracts': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH']},
                    'FEATURE_PROGRAMMATIC__shared.iter_formal_claims': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE']},
                    'FEATURE_PROGRAMMATIC__shared.parse_native_model_claim': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE', 'LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH']},
                    'FEATURE_PROGRAMMATIC__shared.validate_aspect_hierarchy': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH']},
                    'FEATURE_PROGRAMMATIC__shared.validate_aspect_instance': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH']},
                    'FEATURE_PROGRAMMATIC__shared.validate_dependencies_claim': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH']},
                    'FEATURE_PROGRAMMATIC__shared.verify_packaged_dependencies_check': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE']},
                },
            },
        },
    ),
)
```
