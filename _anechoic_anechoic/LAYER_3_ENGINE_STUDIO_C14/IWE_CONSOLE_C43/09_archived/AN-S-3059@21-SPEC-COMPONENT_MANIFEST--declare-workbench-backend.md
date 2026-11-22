---
atom_family: SPEC
atom_id: AN-S-3059
container:
  component: C43
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 21
  updated_at: "2026-11-22T07:19:41.172806+00:00"
---

## Summary

Declare WORKBENCH_BACKEND

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C45',
        name='WORKBENCH_BACKEND',
        lens_whitelist=['DES', 'DES/DOM', 'DevOps', 'QA', 'SPEC', 'SWD'],
        boundaries={
            'code': {
                'imports': [
                    'FEATURE_TOOLS__pub.LIFECYCLE_TOOLS',
                    'FEATURE_TOOLS__pub.bind_native_runtime',
                    'FEATURE_TOOLS__pub.execute_native_lifecycle',
                    'FEATURE_TOOLS__pub.resolve_native_project',
                    'FEATURE_TOOLS__pub.rebind_native_selection',
                    'MANIFEST_RUNTIME_C62__shared.run_manifest_runtime',
                    'model_host_pkg2__pub.reviewed_native_model',
                    'project_selection.resolve_project',
                    'import_graph__shared.Source',
                    'source_watcher__pub.SourceWatcher',
                    'carrier_body__pub.frontmatter_bounds',
                    'carrier_body__pub.source_body',
                    'content_records__pub.content_record_span',
                    'content_records__pub.records_by_path',
                    'content_records__pub.value_excluding_declared_children',
                    'markdown_content__pub.content_key',
                    'markdown_content__pub.content_lines',
                    'markdown_content__pub.direct_markdown',
                    'markdown_content__pub.formal_claim_fences',
                    'markdown_content__pub.parse_content',
                    'markdown_content__pub.section_markdown',
                    'markdown_content__pub.source_markdown',
                    'native_source_rows__pub.NativeCapture',
                    'native_source_rows__pub.NativeManifestChanged',
                    'native_source_rows__pub.capture_native',
                    'native_source_rows__pub.check_native_manifest',
                    'source_row__pub.atom',
                    'source_row__pub.canonical',
                    'source_row__pub.canonical_row',
                    'source_row__pub.json_value',
                    'code_access_rules__pub.module_visibility',
                    'component_manifest__pub.parse_component_manifest',
                    'model_catalog__pub.bindings_from_workbench_rows',
                    'native_model_claim__pub.parse_native_model_claim',
                    'package_spec__pub.read_package_spec',
                    'realization_ownership__pub.build_code_access_ownership',
                    'scope_unit_declarations__pub.read_scope_unit_declarations',
                    'carrier_compat__pub.is_current_requirement_declaration',
                    'carrier_compat__pub.matches_carrier_label',
                    'formal_claim_blocks__pub.formal_claim_blocks',
                    'legacy_relation__pub.emits_instance_inverse',
                    'python_claim__pub.parse_structured_python_model_claim',
                    'settings_context__pub.control_root',
                    'settings_context__pub.project_identity',
                    'component_contract__pub.read_component_contract',
                    'scope_carrier__pub.DELEGATION_ROLE_FOLDERS',
                    'scope_carrier__pub.ScopeDeclarationError',
                    'scope_carrier__pub.has_projection_marker',
                    'scope_carrier__pub.has_scope_declaration_form',
                    'subject_notation__pub',
                    'carrier_compat__pub.StatusModelError',
                    'carrier_compat__pub.canonical_status',
                    'carrier_compat__pub.is_logical_container',
                    'carrier_compat__pub.project_root_container_view',
                    'carrier_layout__pub.admitted_parent',
                    'carrier_layout__pub.compile_role_folders',
                    'carrier_layout__pub.derive_filename',
                    'carrier_layout__pub.role_folders_from_orders',
                    'carrier_read__pub.CarrierError',
                    'carrier_read__pub.parse_carrier',
                    'native_carrier_header__pub.native_header_view',
                    'native_carrier_placement__pub.PROJECT_CONFIG_DIRECTORY',
                    'native_carrier_placement__pub.TICKET_DIRECTORY',
                    'atom_reference__pub.atom_identifier',
                    'atom_reference__pub.derive_atom_ref',
                    'carrier_compat__pub.canonical_role_name',
                    'carrier_compat__pub.carrier_read_view',
                    'carrier_compat__pub.carrier_status_folder',
                    'carrier_compat__pub.header_field_paths',
                    'carrier_compat__pub.header_value',
                    'carrier_compat__pub.matches_named_value',
                    'carrier_compat__pub.named_value_token',
                    'carrier_compat__pub.path_value',
                    'structure_host_pkg3__pub.read_structure',
                    'FEATURE_MODEL_VALIDATION__shared.check_code_access',
                    'ADAPTERS_C30__pub.validate_directory_components',
                    'settings_carrier__pub.read_settings_carrier',
                    'journal_settings__pub.configured_journal_root',
                    'journal_settings__pub.journal_storage',
                    'journal_settings__pub.validated_journal_root',
                    'work_journal__pub.MAX_DATABASE_EVENT_BYTES',
                    'work_journal__pub.PROJECT_DATABASE',
                    'work_journal__pub.append_sealed_events',
                    'work_journal__pub.canonical_json_bytes',
                    'work_journal__pub.journal_inbox',
                    'work_journal__pub.pending_database_journal',
                ],
                'exports': {
                    'native_service_owner.NativeQueryOwner': {'private': ['LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP']},
                    'import_cache.read_import_sources': {'private': ['LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'import_tables.publish_imports': {'private': ['LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'spec_trace._read_pins': {'private': ['LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'content_schema.compile_content_schema': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                    'workbench_schema_asset.compile_schema': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                    'workbench_schema_asset.load_image_schema': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                    'workbench_schema_asset.schema_asset': {'private': ['LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                    'FEATURE_WORKBENCH_BACKEND__shared': None,
                    'FEATURE_WORKBENCH_BACKEND__shared.SourceReader': None,
                    'FEATURE_WORKBENCH_BACKEND__shared.boundary_tables': {'private': ['LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP']},
                    'FEATURE_WORKBENCH_BACKEND__shared.realization_projection': {'private': ['LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP']},
                    'FEATURE_WORKBENCH_BACKEND__shared.NativeQueryInputs': {'private': ['LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP']},
                    'FEATURE_WORKBENCH_BACKEND__shared.NativeQueryRuntime': {'private': ['LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP']},
                    'FEATURE_WORKBENCH_BACKEND__pub': 'public',
                    'FEATURE_WORKBENCH_BACKEND__pub.ServiceInterface': 'public',
                    'FEATURE_WORKBENCH_BACKEND__pub.DELIVERY_MODES': 'public',
                    'FEATURE_WORKBENCH_BACKEND__pub.QueryExecutionError': 'public',
                    'FEATURE_WORKBENCH_BACKEND__pub.WorkbenchUnavailableError': 'public',
                },
            },
            'io': {
                'server': {
                    'workbench_api': {
                        'transport': 'http',
                        'socket': 'private Unix socket',
                        'startup': {
                            'module': 'APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.backend_process',
                            'arguments': ['--socket', '<socket>', '--project-root', '<project-root>',
                                          '--control-root', '<control-root>', '--instance-id', '<instance-id>',
                                          '--manifest-sha256', '<manifest-sha256>',
                                          '[--host-project-root <host-project-root>]',
                                          '[--default-workbench-storage <disk|memory>]',
                                          '[--default-journal-storage <files|duckdb>]'],
                        },
                        'routes': {'health': 'GET /health', 'operation': 'POST /workbench'},
                    },
                    'previous_image_model_claim_selection': {
                        'transport': 'cli',
                        'runner': 'docker',
                        'path': 'LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/native_model_selector.py',
                        'entrypoint': '/opt/venv/bin/python',
                        'arguments': ['/selector.py', '/model'],
                    },
                },
            },
            'state': {
                'reads': ['Project Manifest', 'Project carriers', 'accepted Model and Structure'],
                'writes': ['Workbench projection', 'Workspaces', 'query results and logs'],
            },
        },
    ),
)
```
