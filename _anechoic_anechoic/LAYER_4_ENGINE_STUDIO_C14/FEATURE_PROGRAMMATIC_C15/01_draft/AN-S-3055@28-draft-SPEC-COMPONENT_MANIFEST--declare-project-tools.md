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
  status: draft
  version: 28
  updated_at: '2026-11-27T10:55:20+00:00'
---

## Summary

Declare PROJECT_TOOLS

## Purpose

Run and report Project prerequisite, source, and candidate image checks.
Clean Project scratch directories and migrate native Atom Headers in staged copies.

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
{'code': {'imports': ['test_suite__shared.source_comments',
                      'test_suite__shared._test_phase',
                      'test_suite__shared.suite_preflight',
                      'FEATURE_MCP__tests__shared.packaged_identity_reader',
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
                      'ADAPTERS_C30__shared.spec_lens_directories'],
          'exports': {'test_suite__shared.source_comments': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/static']},
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
                                  'path': 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/test_suite__pub.py'},
                   'prune_private_tmp': {'transport': 'cli',
                                         'runner': 'python',
                                         'path': 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/prune_private_tmp.py'},
                   'migrate_native_atom_headers': {'transport': 'cli',
                                                   'runner': 'uv',
                                                   'path': 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/migrate_native_atom_headers.py'}}}}
```

## Component Contract

### Run the Project Test Suite

#### Guarantee

Given a Project root and an optional selection of source test Modules,
run the selected or discovered Modules in fresh Python interpreters.
Report each Module's result and the suite totals on the output streams.

Return exit status zero when the selected suite passes. Return a
nonzero status for an invalid selection, an unavailable required test
environment, or a failed test Module. A skipped required test fails
the suite. C16 owns Project lifecycle operations. C19 executes the checks.

#### Preflight

Use `--phase preflight` to check the locked frontend dependencies,
pinned DuckPGQ extension, and pinned Chromium launch. Report each
unavailable prerequisite and return a nonzero status if any check fails.

#### Static checks

Use `--phase static` to run the source analyzers once and then run
the source tests in `static/` if the analyzers pass. Apply Engine source
quality Standard `AN-S-4739@3`, including the applicable C15 Standards.
Report the source location for each size violation and fail the phase
when a violation occurs.

#### Host functional and unit checks

Use `--phase functional` for the required host Modules in
`tool.anechoic.test_suite.functional_test_modules`. Run them in fresh
interpreters and report the selected Modules and results. Refuse an
empty, invalid, duplicate, or undiscovered selection.

Use `--phase unit` for source-side diagnostic tests. Use repeatable
`--test-module` options to select specific discovered test Modules.

#### Candidate image tests and canary

Use `--phase image-tests` with the Project root and exact candidate
image ID. Use `--phase canary` for a separate MCP canary on the verified
candidate after the required canary host tests pass. The combined
`--phase image` runs image tests before the canary and returns early
when those tests fail.

Supply the staged package, run ID, and `--canary-selection` to the
canary. The selection is a JSON object with `control_root`,
`manifest_path`, `manifest_ref`, `manifest_sha256`, `project_name`,
`project_prefix`, and `query_enabled`. Use `--canary-project-root` to
select a separate target Project.

Verify the pinned Manifest before using the staged Project. Start the
candidate, initialize MCP, and run a representative query. Use MCP
ping when the Project excludes Run Query. Report the loopback MCP
endpoint on success and clean up the disposable candidate resources.

#### Claim

The CLI claim classifies the Test Suite process exit status. The
release test phase claim describes the observable order of successful
checks and the recording of a failed phase before its terminal status.
It covers local validation, including the disposable candidate image.

##### Formal Claim

```python cli
declare_cli_contract(
    interface='test_suite',
    action='run_project_test_suite',
    outcomes={'succeeded': 'zero', 'failed': 'nonzero'},
)
```

```python trace
declare_trace_contract(
    action='run_release_test_phase',
    effects={
        'failed': ('C19', 'failed'),
        'passed': ('C19', 'passed'),
        'preflight': ('prerequisite_checks', 'passed'),
        'static': ('static_checks', 'passed'),
        'functional': ('host_functional_checks', 'passed'),
        'image_tests': ('candidate_image_tests', 'passed'),
        'canary_host': ('canary_host_checks', 'passed'),
        'canary': ('candidate_canary', 'passed'),
    },
    cases={
        'failed': {'must_effect': ('failed',)},
        'preflight_passed': {
            'must_effect': ('preflight', 'passed'),
            'must_precede': (('preflight', 'passed'),),
        },
        'static_passed': {
            'must_effect': ('static', 'passed'),
            'must_precede': (('static', 'passed'),),
        },
        'functional_passed': {
            'must_effect': ('functional', 'passed'),
            'must_precede': (('functional', 'passed'),),
        },
        'image_tests_passed': {
            'must_effect': ('image_tests', 'passed'),
            'must_precede': (('image_tests', 'passed'),),
            'forbid_effect': ('candidate_canary',),
        },
        'canary_passed': {
            'must_effect': ('canary_host', 'canary', 'passed'),
            'must_precede': (('canary_host', 'canary'), ('canary', 'passed')),
            'forbid_effect': ('candidate_image_tests',),
        },
        'image_passed': {
            'must_effect': ('image_tests', 'canary', 'passed'),
            'must_precede': (('image_tests', 'canary'), ('canary', 'passed')),
        },
    },
)
```

### Clean Project scratch directories

Run `prune_private_tmp.py --mark PATH` from a Project checkout to
mark a completed run's private, user-owned directory directly under
`/private/tmp`. Run without `--mark` to remove eligible directories
marked for that checkout after three days.

Before deletion, check Git worktrees, Docker bind mounts, open files,
mounted paths, and the identity and modification time of each
candidate. Report removed paths. Return a nonzero status if the cleanup
checks fail. An empty eligible set succeeds without a deletion.

```python cli
declare_cli_contract(
    interface='prune_private_tmp',
    action='clean_project_scratch',
    outcomes={'succeeded': 'zero', 'failed': 'nonzero'},
)
```

### Migrate staged native Atom Headers

Use the Local Release launcher `migrate_native_atom_headers.py SOURCE
DESTINATION [--recovery FILE]`. C19 reads an existing staged source
directory outside the checkout and writes a new destination outside
the checkout. The optional recovery file maps exact Atom references
to integer Tiers.

Refuse an invalid staged tree, unresolved recovery references, or
destination collisions before writing. On success, preserve the source,
write the migrated tree, and write the adjacent
`DESTINATION.receipt.json` with the carrier conversions.

```python cli
declare_cli_contract(
    interface='migrate_native_atom_headers',
    action='migrate_staged_headers',
    outcomes={'succeeded': 'zero', 'failed': 'nonzero'},
)
```
