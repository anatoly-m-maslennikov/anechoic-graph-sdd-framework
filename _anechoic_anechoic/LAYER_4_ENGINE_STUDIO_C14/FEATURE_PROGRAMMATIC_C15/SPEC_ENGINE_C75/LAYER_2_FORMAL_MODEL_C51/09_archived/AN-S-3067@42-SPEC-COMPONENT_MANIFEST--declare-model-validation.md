---
atom_family: SPEC
atom_id: AN-S-3067
container:
  component: C51
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 42
  updated_at: "2026-11-26T15:52:29.838128+00:00"
---

## Summary

Declare MODEL_VALIDATION

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C53',
    name='MODEL_VALIDATION',
    lens_whitelist=['DES'],
)
```

## Component Boundaries

```python
{'code': {'imports': ['ADAPTERS_C30__shared.CodeAccessOwnership',
                      'ADAPTERS_C30__shared.build_code_access_ownership',
                      'FEATURE_GENERATED_MODEL_C52__shared.AtomDestination',
                      'FEATURE_GENERATED_MODEL_C52__shared.AtomDestinationFile',
                      'ADAPTERS_C30__shared.manifest_state_fields',
                      'cardinality__pub.cardinality_bounds',
                      'ADAPTERS_C30__shared.canonical_model_address',
                      'ADAPTERS_C30__shared.bind_ordering_declarations',
                      'ADAPTERS_C30__shared.order_properties',
                      'code_access_rules__pub.module_visibility',
                      'code_access_rules__pub.parse_code_access',
                      'FEATURE_MODEL_VALIDATION__shared.check_code_access',
                      'FEATURE_MODEL_VALIDATION__shared.open_serialized_model',
                      'FEATURE_MODEL_VALIDATION__shared.validate_model_instance',
                      'ADAPTERS_C30__shared.parse_native_model_claim',
                      'ADAPTERS_C30__shared.model_class_target',
                      'ADAPTERS_C30__shared.native_header_view',
                      'atom_reference__pub.derive_atom_ref',
                      'ADAPTERS_C30__shared.ProjectSelectionError',
                      'FEATURE_TOOLS__shared.discover_native_project',
                      'FEATURE_TOOLS__shared.mcp_tool_blacklist',
                      'FEATURE_TOOLS__shared.rebind_native_selection',
                      'FEATURE_MODEL_VALIDATION__shared.bind_model_declarations',
                      'FEATURE_MODEL_VALIDATION__shared.bind_reviewed_instance_check',
                      'FEATURE_MODEL_VALIDATION__shared.derive_declared_sibling_links',
                      'FEATURE_MODEL_VALIDATION__shared.validate_declared_sibling_order',
                      'FEATURE_MODEL_VALIDATION__shared.validate_model_fields',
                      'FEATURE_MODEL_VALIDATION__shared.validate_population_uniqueness',
                      'FEATURE_MODEL_VALIDATION__shared.validate_relation_endpoint_levels'],
          'exports': {'FEATURE_MODEL_VALIDATION__shared.open_serialized_model': {'private': ['C16',
                                                                                             'CS1',
                                                                                             'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.open_admitted_model': {'private': ['C75', 'C16',
                                                                                           'C62',
                                                                                           'CS1',
                                                                                           'CS2',
                                                                                           'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/functional']},
                      'model_declaration_bindings.bind_model_declarations': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.verify_model': {'private': ['CS1',
                                                                                    'CS2']},
                      'FEATURE_MODEL_VALIDATION__shared': None,
                      'FEATURE_MODEL_VALIDATION__shared.BoundNativeModel': {'private': ['C50']},
                      'FEATURE_MODEL_VALIDATION__shared.validate_model_instance': {'private': ['C50',
                                                                                               'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests',
                                                                                               'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.bind_model_declarations': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests',
                                                                                              'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'model_field_validation.validate_model_fields': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests',
                                                                                   'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.bind_reviewed_instance_check': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.check_code_access': {'shared': ['C59',
                                                                                        'C61',
                                                                                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.effective_relation_constraints': None,
                      'FEATURE_MODEL_VALIDATION__shared.validate_relation_endpoint_levels': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.derive_declared_sibling_links': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.validate_declared_sibling_order': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.validate_model_fields': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.validate_population_uniqueness': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.validate_relation_targets': None,
                      'FEATURE_MODEL_VALIDATION__pub': 'public',
                      'FEATURE_MODEL_VALIDATION__pub.validate_model_instance': 'public',
                      'FEATURE_MODEL_VALIDATION__pub.BoundNativeModel': 'public',
                      'FEATURE_MODEL_VALIDATION__shared.normalize_reviewed_claim': None,
                      'FEATURE_MODEL_VALIDATION__shared.reviewed_claim_sha256': None}},
 'io': {'server': {'project_admission': {'transport': 'json_lines',
                                         'runner': 'managed_python',
                                         'module': 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.project_admission__pub',
                                         'input_fields': ['project_root',
                                                          'control_root',
                                                          'instance_id',
                                                          'host_root'],
                                         'output': 'admitted Project '
                                                   'binding and Tool '
                                                   'policy, or Project '
                                                   'selection error'}},
        'client': {'reviewed_model': {'transport': 'cli',
                                      'runner': 'managed_python',
                                      'module': 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.image_model_compile'}}}}
```

## Component Contract

### Validate a proposed Model instance

#### Guarantee

Given a proposed instance and the applicable Model Declarations, validate the
supplied Properties and outgoing Relations against their declared types, allowed
values, cardinalities, and endpoint constraints where applicable. Apply named
instance checks and declared uniqueness rules, including inherited uniqueness
rules, against the supplied peer populations.

Return the constructed Model instance if validation succeeds. Report a
validation error if a rule fails. The caller is responsible for writing the
validated instance.

#### References

AN-S-2292, AN-S-3067, and AN-T-2947.
