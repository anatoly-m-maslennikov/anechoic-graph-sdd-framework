---
atom_family: SPEC
atom_id: AN-S-3055
container:
  component: C15
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 31
  updated_at: "2026-11-28T11:49:06+00:00"
---

## Summary

Declare PROJECT_TOOLS

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C19',
    name='PROJECT_TOOLS',
    lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': ['source_sizes',
                      'functional_history.select_fast',
                      'suite_cli.run_phase',
                      'suite_report.suite_report',
                      'test_suite__shared.source_comments',
                      'test_suite__shared._test_phase',
                      'test_suite__shared.suite_preflight',
                      'FEATURE_MCP__tests__shared.packaged_identity_reader',
                      'ADAPTERS_C30__shared.owned_temporary_root',
                      'ADAPTERS_C30__shared.read_scope_unit_declarations',
                      'ADAPTERS_C30__shared.capture_native',
                      'ADAPTERS_C30__shared.active_spec_directories',
                      'carrier_syntax__pub.parse_carrier_syntax',
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
                      'ADAPTERS_C30__shared.spec_lens_directories'],
          'exports': {'source_sizes': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/static']},
                      'functional_history.select_fast': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests']},
                      'suite_cli.run_phase': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests']},
                      'suite_report.suite_report': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests']},
                      'test_suite__shared.source_comments': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/static']},
                      'test_suite__shared._test_phase': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests']},
                      'test_suite__shared.suite_preflight': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/unit']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.ANALYSIS': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                                                                'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.BASE': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.CLASSIFICATION_CFEL_BODY': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                                                                                                                                'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.CLASSIFICATION_PYTHON_BODY': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests',
                                                                                                                                  'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.CONTENT_PROPERTY': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                                                                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.DEPENDENCIES': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                    'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.EVENT_CLAIM': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                   'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.EVENT_CLASS': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                   'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.FALLBACK_CLAIM': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                      'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.FALLBACK_PLAN': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.FALLBACK_PROJECT': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.FALLBACK_PROP': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                     'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.FORM_EXAMPLES': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                     'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.HEADER_RELATIONS': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.INSTANCE_CHECK': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                      'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.NESTED_CONTENT': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                                                                      'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.NESTED_HEADER': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                                                                     'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.PROJECT': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.RECURSIVE_CONTENT': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                         'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                                                                         'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.ROLE': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                                                            'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.ROLE_HEADER': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                   'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                                                                   'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.SEQ': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                           'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.SEQUENCE_CLAIM': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                      'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.SEQUENCE_PLAN': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                     'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.SEQUENCE_PROP': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.STATUS_GROUPS': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                     'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.STATUS_PLAN': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                   'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.THRESHOLD': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.WORKSPACE': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests',
                                                                                                                 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/GENERATE_ENTITY_GRAPH__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.extension_directory': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests',
                                                                                                                           'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.polling_source_watcher': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.render_scope_declaration': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.source_path': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.validate_manifest': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                                                                         'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.write_atom': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.write_scope_unit_declarations': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests',
                                                                                                                                     'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/COMPILE_APPLICABLE_METHODOLOGY/COMPILE_APPLICABLE_METHODOLOGY__tests',
                                                                                                                                     'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                                                                                     'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/RELEASE_VERSION/RELEASE_VERSION__tests',
                                                                                                                                     'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests',
                                                                                                                                     'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared.write_settings': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'test_suite__shared': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests',
                                                         'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/unit']},
                      'test_suite__shared.static_checks': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/static']},
                      'test_suite__shared.CODE_ROOTS': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/static']},
                      'test_suite__shared.run_full_suite': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/static']},
                      'test_suite__shared.APP': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests']},
                      'test_suite__shared._release_canary': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests',
                                                                         'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/unit']},
                      'test_suite__shared.full_suite_docker': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests']},
                      'test_suite__shared.prune_private_tmp': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests']},
                      'test_suite__shared.source_line_length': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/static']},
                      'test_suite__shared.python_findings': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/static']},
                      'test_suite__shared.shell_findings': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/static']},
                      'test_suite__shared.unsafe': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/static']},
                      'test_suite__shared.yaml_findings': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/static']},
                      'test_suite__shared.check_functions': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/static']},
                      'test_suite__shared.check_module': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/static']},
                      'test_suite__shared.python_functions': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/static']},
                      'test_suite__shared.web_functions': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/static']},
                      'test_suite__pub': 'public'}},
 'io': {'client': [{'component': 'C46',
                    'interface': 'source_function_sizes'},
                   {'component': 'C61', 'interface': 'import_ownership'},
                   {'component': 'C59', 'interface': 'state_lint'},
                   {'component': 'C63',
                    'interface': 'test_packaged_image_identity'},
                   {'component': 'C21',
                    'interface': 'candidate_test_image_build'},
                   {'component': 'C21',
                    'interface': 'candidate_test_image_cleanup'}],
        'server': {'test_suite': {'transport': 'cli',
                                  'runner': 'uv',
                                  'path': 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/test_suite__pub.py'}}}}
```

## Component Contract

### Run the Project Test Suite

#### Guarantee

Given a Project root and an optional selection of source test Modules,
run the discovered or selected tests in fresh Python interpreters.
Report each Module's result and the suite totals on the output streams.

Return zero when the selected suite passes. Return a nonzero status when
selection, the required test environment, or a test Module fails. A
skipped required test fails the suite.

#### Static checks

Run Ruff's unused-import check (F401) on the active Python source roots.
Use `--phase static` to run source analysis and tests in `static/`. Run the source analyzers once.
Check PROGRAMMATIC source by default. When `enforce_source_size` is
enabled, extend the check to the Test Suite source roots. Refuse modules
above 6 KiB (6,144 source bytes) or functions above 45 nonblank lines.
Use the locked frontend parser for web functions.

#### Host functional checks

Use `--phase functional` to run the required host Modules configured in
`tool.anechoic.test_suite.functional_test_modules`. Run them in fresh
interpreters. Report the selected Modules and results through the normal
Test Suite output.

Refuse empty, invalid, duplicate, or undiscovered selections. A skipped
required test fails the gate.

Use `--phase unit` to run source-side diagnostic tests and
`--test-module` to focus that run.

#### Image tests and canary

Run `--phase image-tests` with the Project root and exact candidate image ID.
Run `--phase canary` for a separate MCP canary on that verified candidate.
The combined `--phase image` runs image tests before the canary.

For the canary, supply the staged package, run ID, and `--canary-selection`.
The selection is a JSON object with `control_root`, `manifest_path`,
`manifest_ref`, `manifest_sha256`, `project_name`, `project_prefix`, and
`query_enabled`. Use `--canary-project-root` for a separate target Project.

Verify the pinned Manifest before using the staged Project. Start the
candidate, initialize MCP, and run a representative query. Use MCP ping
when the Project excludes Run Query. Report the loopback MCP endpoint
on success and clean up the disposable candidate resources.

#### References

AN-S-3290, AN-T-2944, and AN-T-2958.
