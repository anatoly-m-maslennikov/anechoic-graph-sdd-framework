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
  status: archived
  version: 11
  updated_at: '2026-11-22T06:33:19.419659+00:00'
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
                    'topic_dependencies__pub.DEPENDENCIES_CHECK_SOURCE_SHA256',
                    'topic_dependencies__pub.validate_dependencies_claim',
                    'dataclass_field_contract__pub.has_dataclass_field_contracts',
                    'dataclass_field_contract__pub.validate_field_contracts',
                    'model_class_subject__pub.canonical_model_address',
                    'model_class_subject__pub.simple_model_address',
                    'placement_claim__pub.parse_placement_rules',
                    'markdown_content__pub.content_key',
                    'markdown_content__pub.formal_claim_fences',
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
                    'lint_python_model_claim__pub.resolve_model_claim_reference': {'private': ['C50']},
                    'native_model_lint__pub.lint_native_model_claim': {'private': ['C50']},
                    'formal_claim_blocks__pub.formal_claim_blocks': {'private': ['LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND']},
                    'FEATURE_PROGRAMMATIC__shared.Atom': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                    'FEATURE_PROGRAMMATIC__shared.DEPENDENCIES_CLAIM_SHA256': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                    'FEATURE_PROGRAMMATIC__shared.dependencies_are_distinct': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                    'FEATURE_PROGRAMMATIC__shared.verify_packaged_dependencies_check': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                },
            },
        },
    ),
)
```
