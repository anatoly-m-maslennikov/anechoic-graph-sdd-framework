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
  status: active
  version: 44
  updated_at: '2026-11-27T13:12:55.647486+00:00'
---

## Summary

Declare MODEL_VALIDATION

## Purpose

Validate proposed Model instances and open admitted Models for callers.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(component_id='C53', name='MODEL_VALIDATION', lens_whitelist=['DES'])
```

## Component Boundaries

```python
{'code': {'exports': {'admission._package__shared.BoundNativeModel': {'private': ['C53']}, 'admission._package__shared.is_reviewed_claim': {'private': ['C53']}, 'admission._package__shared.normalize_reviewed_claim': {'private': ['C53']}, 'admission._package__shared.bind_reviewed_instance_check': {'private': ['C53']}, 'access._package__shared.check_code_access': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_query/query_database', 'C53', 'C59', 'C61', 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION']}, 'model_rules._package__shared.derive_declared_sibling_links': {'private': ['C53']}, 'model_rules._package__shared.validate_declared_sibling_order': {'private': ['C53']}, 'model_rules._package__shared.validate_population_uniqueness': {'private': ['C53']}, 'model_rules._package__shared.validate_relation_endpoint_levels': {'private': ['C53']}, 'admission.reviewed_instance_check.bind_reviewed_instance_check': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']}, 'model_rules.model_ordering_bindings.validate_declared_sibling_order': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']}, 'model_rules.model_ordering_bindings.derive_declared_sibling_links': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']}, 'model_rules.model_relation_endpoints.validate_relation_endpoint_levels': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/model_rules']}, 'model_rules.model_population_validation.validate_population_uniqueness': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/model_rules']}, 'access.code_access_check.check_code_access': {'private': ['C59', 'C61', 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/code_access']}, 'admission.bound_native_model.normalize_reviewed_claim': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/native']}, 'admission.bound_native_model.is_reviewed_claim': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/native']}, 'admission.bound_native_model.BoundNativeModel': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/native']}, 'FEATURE_MODEL_VALIDATION__tests.FEATURE_MODEL_VALIDATION__tests__shared.CodeAccessOccurrence': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/code_access']}, 'model_relation_validation.effective_relation_constraints': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/admission']}, 'validate_model_instance.validate_model_instance': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/admission']}, 'model_generation__pub._validate_binding_descriptor': {'private': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/realization_support/model', 'C71']}, 'model_declaration_bindings._MIGRATED_RUNTIME_NAMES': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/code_access', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/model_rules']},
                      'model_relation_validation.validate_model_relations': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/sources', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/typed_fields', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/ingestion']},
                      'FEATURE_MODEL_VALIDATION__pub': 'public',
                      'FEATURE_MODEL_VALIDATION__pub.BoundNativeModel': 'public',
                      'FEATURE_MODEL_VALIDATION__pub.validate_model_instance': 'public',
                      'FEATURE_MODEL_VALIDATION__shared': None,
                      'FEATURE_MODEL_VALIDATION__shared.BoundNativeModel': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/native', 'C50']},
                      'FEATURE_MODEL_VALIDATION__shared.bind_model_declarations': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties',
                                                                                              'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/code_access', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/model_rules']},
                      'FEATURE_MODEL_VALIDATION__shared.bind_reviewed_instance_check': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/code_access', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/model_rules']},
                      'FEATURE_MODEL_VALIDATION__shared.check_code_access': {'shared': ['C59', 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION',
                                                                                        'C61',
                                                                                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/code_access', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/model_rules']},
                      'FEATURE_MODEL_VALIDATION__shared.derive_declared_sibling_links': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/code_access', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/model_rules']},
                      'FEATURE_MODEL_VALIDATION__shared.effective_relation_constraints': None,
                      'FEATURE_MODEL_VALIDATION__shared.is_reviewed_claim': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/native', 'C50']},
                      'FEATURE_MODEL_VALIDATION__shared.normalize_reviewed_claim': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/native']},
                      'FEATURE_MODEL_VALIDATION__shared.open_admitted_model': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/ingestion', 'C75',
                                                                                           'C16',
                                                                                           'C62',
                                                                                           'CS1',
                                                                                           'CS2',
                                                                                           'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/functional']},
                      'FEATURE_MODEL_VALIDATION__shared.open_serialized_model': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/ingestion', 'C16',
                                                                                             'CS1',
                                                                                             'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/code_access', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/model_rules']},
                      'FEATURE_MODEL_VALIDATION__shared.reviewed_claim_sha256': None,
                      'FEATURE_MODEL_VALIDATION__shared.validate_declared_sibling_order': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/code_access', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/model_rules']},
                      'FEATURE_MODEL_VALIDATION__shared.validate_model_fields': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/code_access', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/model_rules']},
                      'FEATURE_MODEL_VALIDATION__shared.validate_model_instance': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/native', 'C50',
                                                                                               'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties',
                                                                                               'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/code_access', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/model_rules']},
                      'FEATURE_MODEL_VALIDATION__shared.validate_population_uniqueness': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/code_access', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/model_rules']},
                      'FEATURE_MODEL_VALIDATION__shared.validate_relation_endpoint_levels': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/sources', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/typed_fields', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/ingestion',
                                                                                                                  'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/code_access', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests/model_rules']},
                      'FEATURE_MODEL_VALIDATION__shared.validate_relation_targets': None,
                      'FEATURE_MODEL_VALIDATION__shared.verify_model': {'private': ['CS1', 'CS2']},
                      'model_declaration_bindings.bind_model_declarations': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/admission']},
                      'model_field_validation.validate_model_fields': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests',
                                                                                   'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties']}},
          'imports': ['PROJECT_SUPPORT.PROJECT_SELECTION.PROJECT_SELECTION__shared.discover_native_project', 'PROJECT_SUPPORT.PROJECT_SELECTION.PROJECT_SELECTION__shared.rebind_native_selection', 'PROJECT_SUPPORT.RUNTIME_SUPPORT.RUNTIME_SUPPORT__shared.mcp_tool_blacklist', 'carriers.content.atom_reference__pub.derive_atom_ref', 'carriers.content.atom_reference__pub.is_native_atom_reference', 'carriers.header.header__shared.status_domains', 'model.cardinality__pub.cardinality_bounds', 'structure.code_access_rules__pub.module_visibility', 'structure.code_access_rules__pub.parse_code_access', 'structure.structure__shared.CodeAccessOwnership', 'admission._package__shared.BoundNativeModel', 'admission._package__shared.is_reviewed_claim', 'admission._package__shared.normalize_reviewed_claim', 'admission._package__shared.bind_reviewed_instance_check', 'access._package__shared.check_code_access', 'model_rules._package__shared.derive_declared_sibling_links', 'model_rules._package__shared.validate_declared_sibling_order', 'model_rules._package__shared.validate_population_uniqueness', 'model_rules._package__shared.validate_relation_endpoint_levels',
                      'FEATURE_MODEL_VALIDATION__tests.FEATURE_MODEL_VALIDATION__tests__shared.CodeAccessOccurrence',
                      'model_declaration_bindings.bind_model_declarations',
                      'model_relation_validation.effective_relation_constraints',
                      'validate_model_instance.validate_model_instance','access.code_access_check.check_code_access', 'admission.reviewed_instance_check.bind_reviewed_instance_check', 'model_rules.model_ordering_bindings.derive_declared_sibling_links', 'model_rules.model_ordering_bindings.validate_declared_sibling_order', 'model_rules.model_population_validation.validate_population_uniqueness', 'model_rules.model_relation_endpoints.validate_relation_endpoint_levels', 'ADAPTERS_C30__shared.CodeAccessOwnership',
                      'ADAPTERS_C30__shared.build_code_access_ownership',
                      'FEATURE_GENERATED_MODEL_C52__shared.AtomDestination',
                      'FEATURE_GENERATED_MODEL_C52__shared.AtomDestinationFile',
                      'ADAPTERS_C30__shared.manifest_state_fields',
                      'cardinality__pub.cardinality_bounds',
                      'ADAPTERS_C30__shared.canonical_model_address',
                      'ADAPTERS_C30__shared.status_domains',
                      'ADAPTERS_C30__shared.bind_ordering_declarations',
                      'ADAPTERS_C30__shared.order_properties',
                      'code_access_rules__pub.module_visibility',
                      'code_access_rules__pub.parse_code_access',
                      'FEATURE_MODEL_VALIDATION__shared.check_code_access',
                      'FEATURE_MODEL_VALIDATION__shared.open_serialized_model',
                      'FEATURE_MODEL_VALIDATION__shared.validate_model_instance',
                      'model_declaration_bindings._MIGRATED_RUNTIME_NAMES',
                      'ADAPTERS_C30__shared.parse_native_model_claim',
                      'ADAPTERS_C30__shared.model_class_target',
                      'ADAPTERS_C30__shared.native_header_view',
                      'atom_reference__pub.derive_atom_ref',
                      'atom_reference__pub.is_native_atom_reference',
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
                      'FEATURE_MODEL_VALIDATION__shared.validate_relation_endpoint_levels']},
 'io': {'server': {'admitted_model': {'transport': 'in_process',
                                      'entry': 'FEATURE_MODEL_VALIDATION__shared.open_admitted_model'},
                   'open_admitted_model': {'outcomes': {'succeeded': {'must_effect': [('C53.admitted_model',
                                                                                       'opened')]},
                                                        'failed': {'must_effect': [('C53.admitted_model',
                                                                                    'failed')]}}},
                   'proposed_model_instance': {'transport': 'in_process',
                                               'entry': 'FEATURE_MODEL_VALIDATION__shared.validate_model_instance'},
                   'validate_proposed_model_instance': {'outcomes': {'succeeded': {'must_effect': [('model_rules',
                                                                                                    'passed')],
                                                                                   'forbid_effect': ['instance_write']},
                                                                     'failed': {'must_effect': [('validation',
                                                                                                 'rejected')],
                                                                                'forbid_effect': ['instance_write']}}},
                   'project_admission': {'transport': 'json_lines',
                                         'runner': 'managed_python',
                                         'module': 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.project_admission__pub',
                                         'input_fields': ['project_root',
                                                          'control_root',
                                                          'instance_id',
                                                          'host_root'],
                                         'output': 'admitted Project binding and Tool policy, or '
                                                   'Project selection error'}},
        'client': {'reviewed_model': {'transport': 'cli',
                                      'runner': 'managed_python',
                                      'module': 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.image_model_compile'}}}}
```

## Component Contract

For a successful Model opening, verify the supplied Model fingerprint and
descriptor SHA-256, and bind and yield the verified Model.
The descriptor SHA-256 attests the bytes opened; the yielded Model carries
the fingerprint. At `open_succeeded`, observe the yielded fingerprint and
the digest of the verified bytes. Do not require the yielded Model to carry
the descriptor digest. Compare independently observed values. Missing
observations leave identity unresolved.

Select Project SPEC templates and Atom Status domains from the admitted
Model. Check template creation eligibility only for new Atoms.

```python trace
declare_trace_contract(
    action='validate_proposed_model_instance',
    interface='proposed_model_instance',
    transport='in_process',
    output='succeeded',
    must_effect=(('model_rules', 'passed'),),
    forbid_effect=('instance_write',),
)
```

```python trace
declare_trace_contract(
    action='validate_proposed_model_instance',
    interface='proposed_model_instance',
    transport='in_process',
    output='failed',
    must_effect=(('validation', 'rejected'),),
    forbid_effect=('instance_write',),
)
```

```python trace
declare_trace_contract(
    action='open_admitted_model',
    interface='admitted_model',
    transport='in_process',
    output='succeeded',
    must_effect=(('C53.admitted_model', 'opened'),),
    same_values=(
        (('open_requested', 'model_sha256'), ('admitted_model_opened', 'model_sha256')),
        (('admitted_model_opened', 'model_sha256'), ('open_succeeded', 'model_sha256')),
        (('open_requested', 'descriptor_sha256'), ('admitted_model_opened', 'descriptor_sha256')),
        (('admitted_model_opened', 'descriptor_sha256'), ('open_succeeded', 'descriptor_sha256')),
    ),
    value_types={('open_requested', 'model_sha256'): 'nonempty_string',
                 ('open_requested', 'descriptor_sha256'): 'nonempty_string'},
)
```

```python trace
declare_trace_contract(
    action='open_admitted_model',
    interface='admitted_model',
    transport='in_process',
    output='failed',
    must_effect=(('C53.admitted_model', 'failed'),),
)
```
