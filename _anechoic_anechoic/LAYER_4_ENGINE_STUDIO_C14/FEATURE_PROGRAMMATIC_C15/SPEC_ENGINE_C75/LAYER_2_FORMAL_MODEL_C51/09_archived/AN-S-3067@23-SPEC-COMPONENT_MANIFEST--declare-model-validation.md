---
atom_family: SPEC
atom_id: AN-S-3067
container:
  component: C51
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 23
  updated_at: "2026-11-22T14:12:14.077505+00:00"
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
                    'FEATURE_GENERATED_MODEL_C52.AtomDestination',
                    'FEATURE_GENERATED_MODEL_C52.AtomDestinationFile',
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
                    'FEATURE_TOOLS__pub.ProjectSelectionError',
                    'FEATURE_TOOLS__pub.discover_native_project',
                    'FEATURE_TOOLS__pub.mcp_tool_blacklist',
                    'FEATURE_TOOLS__pub.rebind_native_selection',
                ],
                'exports': {
                    'model_declaration_bindings.bind_model_declarations': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                    'model_generation__pub.open_admitted_model': {'private': ['C62', 'CS1', 'CS2']},
                    'model_generation__pub.verify_model': {'private': ['CS1', 'CS2']},
                    'FEATURE_MODEL_VALIDATION__shared': None,
                    'FEATURE_MODEL_VALIDATION__shared.bind_model_declarations': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests']},
                    'model_field_validation.validate_model_fields': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests']},
                    'FEATURE_MODEL_VALIDATION__shared.bind_reviewed_instance_check': None,
                    'FEATURE_MODEL_VALIDATION__shared.check_code_access': {'shared': ['C59']},
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
            'io': {'server': {'project_admission': {'transport': 'json_lines',
                                              'runner': 'managed_python',
                                              'module': 'FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.project_admission__pub',
                                              'input_fields': ['project_root',
                                                               'control_root',
                                                               'instance_id',
                                                               'host_root'],
                                              'output': 'admitted Project binding and Tool '
                                                        'policy, or Project selection error'}},
             'client': {'reviewed_model': {'transport': 'cli',
                                           'runner': 'managed_python',
                                           'module': 'FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.image_model_compile'}}},
        },
    ),
)
```
