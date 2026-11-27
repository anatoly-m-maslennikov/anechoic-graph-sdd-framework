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
  version: 43
  updated_at: '2026-11-27T01:04:20.461163+00:00'
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
{'code': {'exports': {'model_declaration_bindings._MIGRATED_RUNTIME_NAMES': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'model_relation_validation.validate_model_relations': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests']},
                      'FEATURE_MODEL_VALIDATION__pub': 'public',
                      'FEATURE_MODEL_VALIDATION__pub.BoundNativeModel': 'public',
                      'FEATURE_MODEL_VALIDATION__pub.validate_model_instance': 'public',
                      'FEATURE_MODEL_VALIDATION__shared': None,
                      'FEATURE_MODEL_VALIDATION__shared.BoundNativeModel': {'private': ['C50']},
                      'FEATURE_MODEL_VALIDATION__shared.bind_model_declarations': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests',
                                                                                              'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.bind_reviewed_instance_check': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.check_code_access': {'shared': ['C59',
                                                                                        'C61',
                                                                                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.derive_declared_sibling_links': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.effective_relation_constraints': None,
                      'FEATURE_MODEL_VALIDATION__shared.is_reviewed_claim': {'private': ['C50']},
                      'FEATURE_MODEL_VALIDATION__shared.normalize_reviewed_claim': None,
                      'FEATURE_MODEL_VALIDATION__shared.open_admitted_model': {'private': ['C75',
                                                                                           'C16',
                                                                                           'C62',
                                                                                           'CS1',
                                                                                           'CS2',
                                                                                           'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/functional']},
                      'FEATURE_MODEL_VALIDATION__shared.open_serialized_model': {'private': ['C16',
                                                                                             'CS1',
                                                                                             'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.reviewed_claim_sha256': None,
                      'FEATURE_MODEL_VALIDATION__shared.validate_declared_sibling_order': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.validate_model_fields': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.validate_model_instance': {'private': ['C50',
                                                                                               'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests',
                                                                                               'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.validate_population_uniqueness': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.validate_relation_endpoint_levels': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests',
                                                                                                                  'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_MODEL_VALIDATION__shared.validate_relation_targets': None,
                      'FEATURE_MODEL_VALIDATION__shared.verify_model': {'private': ['CS1', 'CS2']},
                      'model_declaration_bindings.bind_model_declarations': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                      'model_field_validation.validate_model_fields': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests',
                                                                                   'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests']}},
          'imports': ['ADAPTERS_C30__shared.CodeAccessOwnership',
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
