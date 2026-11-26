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
  status: draft
  version: 41
  updated_at: '2026-11-24T17:50:59+00:00'
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
                    'ADAPTERS_C30__shared.parse_native_model_claim',
                    'ADAPTERS_C30__shared.model_class_target',
                    'ADAPTERS_C30__shared.native_header_view',
                    'atom_reference__pub.derive_atom_ref',
                    'ADAPTERS_C30__shared.ProjectSelectionError',
                    'FEATURE_TOOLS__shared.discover_native_project',
                    'FEATURE_TOOLS__shared.mcp_tool_blacklist',
                    'FEATURE_TOOLS__shared.rebind_native_selection',
                ],
            },
            'io': {'server': {'admitted_model': {
                                  'transport': 'in_process',
                                  'entry': 'FEATURE_MODEL_VALIDATION__shared.open_admitted_model',
                              },
                              'open_admitted_model': {'outcomes': {
                                  'succeeded': {'must_effect': [('C53.admitted_model', 'opened')]},
                                  'failed': {'must_effect': [('C53.admitted_model', 'failed')]},
                              }},
                              'validate_proposed_model_instance': {'outcomes': {
                                  'succeeded': {'must_effect': [('model_rules', 'passed')],
                                                'forbid_effect': ['instance_write']},
                                  'failed': {'must_effect': [('validation', 'rejected')],
                                             'forbid_effect': ['instance_write']},
                              }},
                              'project_admission': {'transport': 'json_lines',
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
