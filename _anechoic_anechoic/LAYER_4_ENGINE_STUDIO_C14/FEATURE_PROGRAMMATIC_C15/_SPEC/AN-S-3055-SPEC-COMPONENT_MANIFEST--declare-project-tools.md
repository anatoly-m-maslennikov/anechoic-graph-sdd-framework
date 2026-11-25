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
  status: active
  version: 24
  updated_at: "2026-11-24T23:12:55.813309+00:00"
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
                    'ADAPTERS_C30__shared.owned_temporary_root',
                    'ADAPTERS_C30__shared.read_scope_unit_declarations',
                    'ADAPTERS_C30__shared.capture_native',
                    'ADAPTERS_C30__shared.active_spec_directories',
                    'test_suite__shared.APP',
                    'test_suite__shared._release_canary',
                    'test_suite__shared.full_suite_docker',
                    'test_suite__shared.prune_private_tmp',
                    'test_suite__shared.source_line_length',
                    'test_suite__shared.python_findings',
                    'test_suite__shared.shell_findings',
                    'test_suite__shared.unsafe',
                    'test_suite__shared.yaml_findings',
                    'test_suite__shared.check_functions',
                    'test_suite__shared.check_module',
                    'test_suite__shared.python_functions',
                    'test_suite__shared.web_functions',
                    'test_suite__shared',
                    'test_suite__shared.static_checks',
                    'ADAPTERS_C30__shared.project_goal_filename',
                    'test_suite__shared.CODE_ROOTS',
                    'test_suite__shared.run_full_suite',
                    'model_field_validation.validate_model_fields',
                    'model_host_CS2__shared.reviewed_native_model',
                    'native_workflow_definition.bind_status_specifications',
                    'ADAPTERS_C30__shared.canonical_native_header',
                    'ADAPTERS_C30__shared.native_header_view',
                    'ADAPTERS_C30__shared.ARCHIVE_DIRECTORY',
                    'ADAPTERS_C30__shared.COMPLETE_DIRECTORY',
                    'ADAPTERS_C30__shared.DRAFT_DIRECTORY',
                    'ADAPTERS_C30__shared.PROJECT_CONFIG_DIRECTORY',
                    'ADAPTERS_C30__shared.READY_DIRECTORY',
                    'ADAPTERS_C30__shared.TICKET_DIRECTORY',
                    'ADAPTERS_C30__shared.native_ticket_asset',
                    'ADAPTERS_C30__shared.spec_lens_directories',
                ],
            },
            'io': {
                'client': [
                    {'component': 'C46', 'interface': 'source_function_sizes'},
                    {'component': 'C61', 'interface': 'import_ownership'},
                    {'component': 'C59', 'interface': 'state_lint'},
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
