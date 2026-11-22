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
  version: 7
  updated_at: "2026-11-22T03:15:20.905232+00:00"
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
                    'formal_claim__pub.formal_claim',
                    'model_catalog__pub.class_bindings',
                    'native_model_claim__pub.parse_native_model_claim',
                    'native_model_claim__pub.validate_aspect_hierarchy',
                    'native_model_claim__pub.validate_aspect_instance',
                    'scope_declaration_parse__pub.ScopeUnitDeclarations',
                    'carrier_compat__pub.is_current_requirement_declaration',
                    'legacy_relation__pub.emits_instance_inverse',
                    'model_class_subject__pub.model_class_target',
                    'python_claim__pub.parse_python_model_claim',
                    'subject_notation__pub',
                    'carrier_read__pub.parse_carrier',
                    'carrier_compat__pub.carrier_read_view',
                    'carrier_compat__pub.matches_named_value',
                    'carrier_compat__pub.named_value_token',
                ],
                'exports': {
                    'legacy_claim_compiler__pub.compile_python_model_claim': {'private': ['LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND']},
                    'FEATURE_PROGRAMMATIC__shared.Atom': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE']},
                    'FEATURE_PROGRAMMATIC__shared.DEPENDENCIES_CLAIM_SHA256': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE']},
                    'FEATURE_PROGRAMMATIC__shared.dependencies_are_distinct': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE']},
                    'FEATURE_PROGRAMMATIC__shared.has_dataclass_field_contracts': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH']},
                    'FEATURE_PROGRAMMATIC__shared.validate_dependencies_claim': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH']},
                    'FEATURE_PROGRAMMATIC__shared.verify_packaged_dependencies_check': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE']},
                },
            },
        },
    ),
)
```
