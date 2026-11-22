---
atom_family: SPEC
atom_id: AN-S-3055
container:
  component: C15
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 14
  updated_at: "2026-11-22T15:27:08.409583+00:00"
---

## Summary

Declare PROJECT_TOOLS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C19',
        name='PROJECT_TOOLS',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'code': {
                'imports': [
                    'model_field_validation.validate_model_fields',
                    'model_host_CS2__shared.reviewed_native_model',
                    'native_workflow_definition.bind_status_specifications',
                    'native_carrier_header__pub',
                    'native_carrier_placement__pub',
                ],
                'exports': {
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.ANALYSIS': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.BASE': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.CLASSIFICATION_CFEL_BODY': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.CLASSIFICATION_PYTHON_BODY': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.CONTENT_PROPERTY': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.DEPENDENCIES': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.EVENT_CLAIM': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.EVENT_CLASS': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.FALLBACK_CLAIM': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.FALLBACK_PLAN': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.FALLBACK_PROJECT': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.FALLBACK_PROP': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.FORM_EXAMPLES': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.HEADER_RELATIONS': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.INSTANCE_CHECK': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.NESTED_CONTENT': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.NESTED_HEADER': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.PROJECT': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.RECURSIVE_CONTENT': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.ROLE': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.ROLE_HEADER': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.SEQ': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.SEQUENCE_CLAIM': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.SEQUENCE_PLAN': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.SEQUENCE_PROP': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.STATUS_GROUPS': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.STATUS_PLAN': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.THRESHOLD': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.WORKSPACE': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.extension_directory': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.polling_source_watcher': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.render_scope_declaration': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.source_path': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.validate_manifest': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.write_atom': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.write_scope_unit_declarations': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/COMPILE_APPLICABLE_METHODOLOGY/COMPILE_APPLICABLE_METHODOLOGY__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/RELEASE_VERSION/RELEASE_VERSION__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests',
                        'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests',
                    ]},
                    'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.write_settings': {'shared': [
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests',
                    ]},
                    'test_suite__pub': 'public',
                    'test_suite__pub.run_full_suite': 'public',
                },
            },
            'io': {
                'client': [
                    {'component': 'C46', 'interface': 'source_function_sizes'},
                    {'component': 'C61', 'interface': 'import_ownership'},
                    {'component': 'C63', 'interface': 'test_packaged_image_identity'},
                    {'component': 'C21', 'interface': 'candidate_test_image_build'},
                    {'component': 'C21', 'interface': 'candidate_test_image_cleanup'},
                ],
                'server': {
                    'test_suite': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/test_suite__pub.py',
                    },
                },
            },
        },
    ),
)
```
