---
atom_family: SPEC
atom_id: AN-S-3065
container:
  component: C51
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 9
  updated_at: "2026-11-22T04:37:07.388927+00:00"
---

## Summary

Declare FORMAL_MODEL_GENERATOR

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C50',
        name='FORMAL_MODEL_GENERATOR',
        lens_whitelist=['DES', 'QA', 'SPEC', 'SWD'],
        boundaries={
            'code': {
                'imports': [
                    'artifact_metadata.atomic_write',
                    'project_selection.resolve_project',
                    'relation_declaration_catalog__pub.build_relation_declaration_catalog',
                    'ADAPTERS_C30__pub.CEILINGS',
                    'ADAPTERS_C30__pub.ReadContext',
                    'ADAPTERS_C30__pub.open_regular',
                    'FEATURE_TOOLS__pub.resolve_native_project',
                    'atom_reference__pub.derive_atom_ref',
                    'cardinality__pub.cardinality_bounds',
                    'carrier_compat__pub.matches_named_value',
                    'carrier_read__pub.parse_carrier',
                    'code_access_rules__pub.parse_code_access',
                    'component_manifest__pub.parse_component_manifest_fields',
                    'dataclass_field_contract__pub.validate_field_contracts',
                    'lint_python_model_claim__pub.resolve_model_claim_reference',
                    'markdown_content__pub.parse_content',
                    'model_class_subject__pub.canonical_model_address',
                    'model_class_subject__pub.model_class_target',
                    'model_class_subject__pub.model_declaration_subject',
                    'model_class_subject__pub.simple_model_address',
                    'model_generation__pub.open_admitted_model',
                    'model_generation__pub.verify_model',
                    'native_carrier_header__pub.native_header_view',
                    'native_carrier_placement__pub.CUSTOM_MODEL_DIRECTORY',
                    'native_carrier_placement__pub.PROJECT_CONFIG_DIRECTORY',
                    'native_model_claim__pub.NativeModelClaimError',
                    'native_model_claim__pub.parse_native_model_claim',
                    'native_model_lint__pub.lint_native_model_claim',
                    'package_spec__pub.read_package_spec',
                    'project_manifest__pub.active_manifest_carriers',
                    'project_manifest__pub.manifest_inputs',
                    'project_manifest__pub.manifest_state_fields',
                    'property_order__pub.order_properties',
                    'subject_notation__pub',
                ],
            },
            'io': {
                'server': {
                    'standalone_model_generate': {
                        'transport': 'cli',
                        'runner': 'managed_python',
                        'module': 'LAYER_3_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.generate_model',
                        'arguments': ['--project-root', '<project-root>', '--output', '<python-file>'],
                    },
                    'manifest_compile': {
                        'transport': 'cli',
                        'runner': 'managed_python',
                        'module': 'LAYER_3_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_pkg1.compiler',
                    },
                    'image_model_compile': {
                        'transport': 'cli',
                        'runner': 'managed_python',
                        'module': 'LAYER_3_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_pkg1.image_model_compile',
                    },
                },
            },
        },
    ),
)
```
