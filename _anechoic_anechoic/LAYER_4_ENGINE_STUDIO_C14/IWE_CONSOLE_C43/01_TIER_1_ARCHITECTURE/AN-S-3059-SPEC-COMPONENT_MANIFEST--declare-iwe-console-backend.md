---
atom_family: SPEC
atom_id: AN-S-3059
container:
  component: C43
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 61
  updated_at: '2026-11-27T01:04:20.461163+00:00'
---

## Summary

Declare IWE_CONSOLE_BACKEND

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C45',
    name='IWE_CONSOLE_BACKEND',
    lens_whitelist=['DES', 'DES/DOM', 'DevOps', 'QA', 'SPEC', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': ['ADAPTERS_C30__shared.ProjectSettingsValueError',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.SourceReader',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.compile_role_folders',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.compile_schema',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.compile_status_groups',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.load_image_schema',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.schema_asset',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.compile_project_schema',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.load_registry_asset',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.registry_asset',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.create_shared_app',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.load_host_runtime_config',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.AuditSnapshot',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.AuditWorker',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.expected_carrier',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.materialize_delta',
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.schema_mode',
                      'ADAPTERS_C30__shared.CarrierError',
                      'ADAPTERS_C30__shared.content_key',
                      'ADAPTERS_C30__shared.content_lines',
                      'ADAPTERS_C30__shared.direct_markdown',
                      'ADAPTERS_C30__shared.formal_claim_fences',
                      'ADAPTERS_C30__shared.parse_carrier',
                      'ADAPTERS_C30__shared.parse_content',
                      'ADAPTERS_C30__shared.section_markdown',
                      'ADAPTERS_C30__shared.source_markdown',
                      'FEATURE_TOOLS__tests__shared.compile_candidate_schema',
                      'FEATURE_TOOLS__tests__shared.load_candidate_schema',
                      'KERNEL_MIXER_C59__shared.ATOM',
                      'KERNEL_MIXER_C59__shared.ContentRule',
                      'KERNEL_MIXER_C59__shared.ContentSchema',
                      'KERNEL_MIXER_C59__shared.DeclarationSource',
                      'KERNEL_MIXER_C59__shared.FormalStatement',
                      'KERNEL_MIXER_C59__shared.QueryExecutionError',
                      'KERNEL_MIXER_C59__shared.SCOPE',
                      'KERNEL_MIXER_C59__shared.WorkbenchUnavailableError',
                      'KERNEL_MIXER_C59__shared._atom_facts',
                      'KERNEL_MIXER_C59__shared._carrier_facts',
                      'KERNEL_MIXER_C59__shared._graph_sources',
                      'KERNEL_MIXER_C59__shared._materialized_atom',
                      'KERNEL_MIXER_C59__shared._materialized_row',
                      'KERNEL_MIXER_C59__shared._outgoing_facts',
                      'KERNEL_MIXER_C59__shared._schema_from_rules',
                      'KERNEL_MIXER_C59__shared._scope_facts',
                      'KERNEL_MIXER_C59__shared._scope_references',
                      'KERNEL_MIXER_C59__shared._source',
                      'KERNEL_MIXER_C59__shared._support_facts',
                      'KERNEL_MIXER_C59__shared._support_for_fact',
                      'KERNEL_MIXER_C59__shared.compile_content_schema',
                      'KERNEL_MIXER_C59__shared.content_schema_from_statements',
                      'KERNEL_MIXER_C59__shared.declaration_statements',
                      'KERNEL_MIXER_C59__shared.materialize',
                      'KERNEL_MIXER_C59__shared.materialize_with_registry',
                      'KERNEL_MIXER_C59__shared.relation_registry',
                      'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests',
                      'KERNEL_MIXER_C59__shared.TABLES',
                      'KERNEL_MIXER_C59__shared._declared_filename_issue',
                      'KERNEL_MIXER_C59__shared.collect_issues',
                      'KERNEL_MIXER_C59__shared.create_tables',
                      'KERNEL_MIXER_C59__shared.publish',
                      'component_metrics.measure_components',
                      'component_metrics.refresh_spec_sizes',
                      'KERNEL_MIXER_C59__shared.content_columns',
                      'content_schema',
                      'content_schema.ContentRule',
                      'content_schema.ContentSchema',
                      'content_schema.DeclarationSource',
                      'content_schema.FormalStatement',
                      'content_schema._schema_from_rules',
                      'content_schema._source',
                      'content_schema.compile_content_schema',
                      'content_schema.content_schema_from_statements',
                      'content_schema.declaration_statements',
                      'declaration_ancestry.compile_ancestry',
                      'declaration_cfel.model_statements',
                      'KERNEL_MIXER_C59__shared.HeaderRule',
                      'KERNEL_MIXER_C59__shared.compile_header_rules',
                      'KERNEL_MIXER_C59__shared.header_declaration_rules',
                      'KERNEL_MIXER_C59__shared.header_rules_from_statements',
                      'KERNEL_MIXER_C59__shared.resolve_header_rules',
                      'errors.QueryExecutionError',
                      'errors.WorkbenchUnavailableError',
                      'graph_store.build_graph',
                      'graph_store.graph_delta_state',
                      'graph_store.graph_relations',
                      'graph_store.graph_state',
                      'KERNEL_MIXER_C59__shared.header_columns',
                      'KERNEL_MIXER_C59__shared.HeaderColumn',
                      'KERNEL_MIXER_C59__shared.HeaderSchema',
                      'KERNEL_MIXER_C59__shared.HeaderSchemaState',
                      'KERNEL_MIXER_C59__shared._matches_format',
                      'KERNEL_MIXER_C59__shared.declared_header_schema',
                      'KERNEL_MIXER_C59__shared.infer_header_schema',
                      'KERNEL_MIXER_C59__shared.clear_import_sources',
                      'KERNEL_MIXER_C59__shared.read_import_sources',
                      'KERNEL_MIXER_C59__shared.replace_import_sources',
                      'KERNEL_MIXER_C59__shared._create_external_imports_view',
                      'KERNEL_MIXER_C59__shared.publish_imports',
                      'KERNEL_MIXER_C59__shared.remove_imports',
                      'KERNEL_MIXER_C59__shared.replace_imports',
                      'index_delta.MaterializationDelta',
                      'native_projection',
                      'native_projection.project_native',
                      'native_projection.project_native_delta',
                      'native_projection.replace_component_metrics',
                      'package_audit',
                      'projection_delta.apply',
                      'projection_delta.snapshot',
                      'KERNEL_MIXER_C59__shared.public_rows',
                      'KERNEL_MIXER_C59__shared.SCOPE_FIELDS',
                      'KERNEL_MIXER_C59__shared.atom_fields',
                      'KERNEL_MIXER_C59__shared.insert_public_rows',
                      'KERNEL_MIXER_C59__shared.projected_rows',
                      'query_log.QueryLog',
                      'query_store.QueryStore',
                      'KERNEL_MIXER_C59__shared.QueryStore',
                      'KERNEL_MIXER_C59__shared._connect',
                      'header_columns.HeaderColumn',
                      'header_columns.HeaderSchema',
                      'relation_declarations.relation_declaration',
                      'KERNEL_MIXER_C59__shared.relation_registry_module',
                      'KERNEL_MIXER_C59__shared.RegistryCompilation',
                      'KERNEL_MIXER_C59__shared.RegistryContribution',
                      'KERNEL_MIXER_C59__shared.RelationRegistry',
                      'KERNEL_MIXER_C59__shared._unambiguous_aliases',
                      'KERNEL_MIXER_C59__shared._warn_colliding_uses',
                      'KERNEL_MIXER_C59__shared.compile_registry',
                      'KERNEL_MIXER_C59__shared.compile_relation_registry',
                      'KERNEL_MIXER_C59__shared.is_registry_declaration',
                      'KERNEL_MIXER_C59__shared.registry_contribution',
                      'KERNEL_MIXER_C59__shared.registry_from_contributions',
                      'KERNEL_MIXER_C59__shared.relations_module',
                      'result_columns.result_columns',
                      'result_delivery.DELIVERY_MODES',
                      'result_files.write_result_file',
                      'saved_queries.SavedQueryStore',
                      'KERNEL_MIXER_C59__shared.archived',
                      'KERNEL_MIXER_C59__shared.filename_role_matches',
                      'KERNEL_MIXER_C59__shared.group',
                      'KERNEL_MIXER_C59__shared.markdown_paths',
                      'KERNEL_MIXER_C59__shared.CANONICAL_ROLE_MARKERS',
                      'KERNEL_MIXER_C59__shared.ROLE_MARKERS',
                      'KERNEL_MIXER_C59__shared.first_reference_rows',
                      'KERNEL_MIXER_C59__shared.PILOT',
                      'KERNEL_MIXER_C59__shared.SpecTraceStore',
                      'import_graph__shared.is_trace_path',
                      'import_graph__shared.native_trace_rows',
                      'KERNEL_MIXER_C59__shared.remove_native_traces',
                      'KERNEL_MIXER_C59__shared.replace_native_traces',
                      'statements.select_statement',
                      'watcher_change_log.WatcherChangeLog',
                      'workspace.WorkspaceStore',
                      'FEATURE_TOOLS__shared.resolve_native_project',
                      'FEATURE_TOOLS__shared.rebind_native_selection',
                      'FEATURE_TOOLS__shared.discover_native_project',
                      'FEATURE_TOOLS__shared.mcp_tool_blacklist',
                      'FEATURE_TOOLS__shared.declared_release_entrypoint',
                      'FEATURE_TOOLS__shared.ExplicitBlockingRuntimeFailure',
                      'FEATURE_TOOLS__pub.ProjectSelectionError',
                      'model_host_CS2__shared.reviewed_native_model',
                      'FEATURE_TOOLS__shared.resolve_project',
                      'import_graph__shared.Source',
                      'import_graph__shared.ImportSite',
                      'ADAPTERS_C30__shared.canonical',
                      'ADAPTERS_C30__shared.ProjectSelectionError',
                      'source_watcher__pub.SourceWatcher',
                      'ADAPTERS_C30__shared.frontmatter_bounds',
                      'ADAPTERS_C30__shared.source_body',
                      'content_records__pub.content_record_span',
                      'content_records__pub.records_by_path',
                      'content_records__pub.value_excluding_declared_children',
                      'markdown_content__pub.parse_content',
                      'ADAPTERS_C30__shared.NativeCapture',
                      'ADAPTERS_C30__shared.NativeManifestChanged',
                      'ADAPTERS_C30__shared.capture_native',
                      'ADAPTERS_C30__shared.check_native_manifest',
                      'source_row__pub.atom',
                      'source_row__pub.canonical',
                      'source_row__pub.canonical_row',
                      'source_row__pub.json_value',
                      'code_access_rules__pub.module_visibility',
                      'component_manifest__pub.parse_component_manifest',
                      'ADAPTERS_C30__shared.bindings_from_workbench_rows',
                      'ADAPTERS_C30__shared.parse_native_model_claim',
                      'realization_ownership__pub.build_code_access_ownership',
                      'ADAPTERS_C30__shared.read_scope_unit_declarations',
                      'ADAPTERS_C30__shared.is_current_requirement_declaration',
                      'ADAPTERS_C30__shared.matches_carrier_label',
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.formal_claim_blocks',
                      'legacy_relation__pub.emits_instance_inverse',
                      'ADAPTERS_C30__shared.parse_structured_python_model_claim',
                      'ADAPTERS_C30__shared.control_root',
                      'ADAPTERS_C30__shared.project_identity',
                      'component_contract__pub.read_component_contract',
                      'ADAPTERS_C30__shared.DELEGATION_ROLE_FOLDERS',
                      'ADAPTERS_C30__shared.ScopeDeclarationError',
                      'ADAPTERS_C30__shared.has_projection_marker',
                      'ADAPTERS_C30__shared.has_scope_declaration_form',
                      'ADAPTERS_C30__shared.Span',
                      'ADAPTERS_C30__shared.Name',
                      'ADAPTERS_C30__shared.ValueLiteral',
                      'ADAPTERS_C30__shared.FormatReference',
                      'ADAPTERS_C30__shared.Cardinality',
                      'ADAPTERS_C30__shared.Qualification',
                      'ADAPTERS_C30__shared.DeclaredReference',
                      'ADAPTERS_C30__shared.SelectionGroup',
                      'ADAPTERS_C30__shared.SelectionSuffix',
                      'ADAPTERS_C30__shared.PathStep',
                      'ADAPTERS_C30__shared.Path',
                      'ADAPTERS_C30__shared.RelationLink',
                      'ADAPTERS_C30__shared.RelationChain',
                      'ADAPTERS_C30__shared.ParsedSubject',
                      'ADAPTERS_C30__shared.parse_subject_expression',
                      'ADAPTERS_C30__shared.render_subject',
                      'ADAPTERS_C30__shared.GrammarSource',
                      'ADAPTERS_C30__shared.GrammarPin',
                      'ADAPTERS_C30__shared.InitialAtomSelector',
                      'ADAPTERS_C30__shared.SubjectNotationError',
                      'ADAPTERS_C30__shared.SubjectProfile',
                      'ADAPTERS_C30__shared.get_profile',
                      'ADAPTERS_C30__shared.namespace_local_expression',
                      'ADAPTERS_C30__shared.parse_initial_atom_selector',
                      'ADAPTERS_C30__shared.parse_subject',
                      'ADAPTERS_C30__shared.profile_evidence',
                      'ADAPTERS_C30__shared.StatusModelError',
                      'ADAPTERS_C30__shared.canonical_status',
                      'ADAPTERS_C30__shared.is_logical_container',
                      'ADAPTERS_C30__shared.project_root_container_view',
                      'ADAPTERS_C30__shared.admitted_parent',
                      'ADAPTERS_C30__shared.compile_role_folders',
                      'ADAPTERS_C30__shared.derive_filename',
                      'ADAPTERS_C30__shared.role_folders_from_orders',
                      'carrier_read__pub.CarrierError',
                      'carrier_read__pub.parse_carrier',
                      'native_carrier_header__pub.native_header_view',
                      'ADAPTERS_C30__shared.PROJECT_CONFIG_DIRECTORY',
                      'ADAPTERS_C30__shared.TICKET_DIRECTORY',
                      'atom_reference__pub.atom_identifier',
                      'atom_reference__pub.derive_atom_ref',
                      'ADAPTERS_C30__shared.canonical_role_name',
                      'ADAPTERS_C30__shared.carrier_read_view',
                      'ADAPTERS_C30__shared.carrier_status_folder',
                      'ADAPTERS_C30__shared.header_field_paths',
                      'ADAPTERS_C30__shared.header_value',
                      'ADAPTERS_C30__shared.matches_named_value',
                      'ADAPTERS_C30__shared.named_value_token',
                      'ADAPTERS_C30__shared.path_value',
                      'ADAPTERS_C30__shared.StructureSnapshot',
                      'ADAPTERS_C30__shared.validate_directory_components',
                      'ADAPTERS_C30__shared.read_settings_carrier',
                      'journal_settings__pub.configured_journal_root',
                      'journal_settings__pub.journal_storage',
                      'journal_settings__pub.validated_journal_root',
                      'work_journal__pub.MAX_DATABASE_EVENT_BYTES',
                      'work_journal__pub.PROJECT_DATABASE',
                      'work_journal__pub.append_sealed_events',
                      'work_journal__pub.canonical_json_bytes',
                      'work_journal__pub.journal_inbox',
                      'work_journal__pub.pending_database_journal'],
          'exports': {'native_model_selector': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.AuditSnapshot': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.AuditWorker': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.expected_carrier': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.materialize_delta': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.schema_mode': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.CHECK': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.LOAD': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.NATIVE_TOOLS': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.PAGE': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.QUERY_LOG_LIST': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.RUN': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.SAVED_LIST': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.SAVE_VIEW': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.SCHEMA': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.SharedToolFrontier': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.SourceReader': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.ToolInputValidationError': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.ToolOutputValidationError': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.ToolRegistryRuntimeError': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.ToolRegistryStaleError': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.VIEW_CREATE': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.VIEW_DUPLICATE': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.WORKSPACE_OPEN': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared._candidate_paths': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.discover_frontier': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.load_active_registry': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.native_tools': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.public_tool': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.shared_project_catalog': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.HostRuntimeConfig': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.HostRuntimeConfigError': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.compile_role_folders': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.compile_schema': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                                       'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.compile_status_groups': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.create_shared_app': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.load_host_runtime_config': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests',
                                                                                                 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.load_image_schema': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                                          'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.resolve_host_project': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.schema_asset': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                                     'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'backend_process._release_command': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'backend_tool_api.tool_failure_result': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'project_admission.project_tool_policy': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'generate_tool_registry.generate': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'registry_lifecycle_provider.LIFECYCLE_TOOL_NAMES': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'registry_lifecycle_provider.NativeLifecycleProvider': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'registry_lifecycle_provider.tool_descriptors': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'registry_release_command_provider.RELEASE_COMMAND_TOOLS': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'registry_workbench_provider.WorkbenchProvider': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'tool_registry_assets.FEATURE_RELATIVE': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'tool_registry_assets.ToolRegistryAssetError': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'tool_registry_assets.read_inventory': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'workbench_links.public_saved': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'workbench_links.public_workspace': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'workbench_links.validate_reference': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'project_tool_session.ToolProtocolError': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'shared_backend_process': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'shared_backend_process.create_app': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'workbench_operations.WorkbenchOperations': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.compile_project_schema': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.load_registry_asset': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared.registry_asset': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_IWE_CONSOLE_BACKEND__shared': None}},
 'io': {'server': {'project_admission': {'transport': 'stdio',
                                         'module': 'APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.project_admission',
                                         'protocol': 'newline-delimited '
                                                     'JSON',
                                         'request_fields': ['project_root',
                                                            'control_root',
                                                            'instance_id',
                                                            'host_root'],
                                         'response_fields': ['result or '
                                                             'error'],
                                         'result_policy_fields': ['tool_blacklist',
                                                                  'release_workflows_enabled']},
                   'read_host_settings': {'transport': 'cli',
                                          'module': 'APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.host_runtime_config',
                                          'arguments': ['[--host-settings '
                                                        '<path>]'],
                                          'response': 'validated host '
                                                      'settings as JSON'},
                   'shared_tool_coordinator': {'transport': 'http',
                                               'socket': 'private Unix '
                                                         'socket',
                                               'startup': {'module': 'APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.shared_backend_process',
                                                           'arguments': ['--socket',
                                                                         '<socket>',
                                                                         '[--host-settings '
                                                                         '<path>]']},
                                               'routes': {'status': 'GET '
                                                                    '/health',
                                                          'selection': 'POST '
                                                                       '/selection',
                                                          'catalog': 'GET '
                                                                     '/tools',
                                                          'invoke': 'POST '
                                                                    '/tools'},
                                               'selection_fields': ['project_root'],
                                               'tool_failure_fields': ['code',
                                                                       'message',
                                                                       'scope',
                                                                       'tool_result'],
                                               'request_fields': ['name',
                                                                  'arguments',
                                                                  'session_id',
                                                                  'public_base_url']},
                   'tool_api': {'transport': 'http',
                                'socket': 'private Unix socket',
                                'routes': {'catalog': 'GET /tools',
                                           'invoke': 'POST /tools'},
                                'catalog_binding': 'instance_id query '
                                                   'parameter',
                                'failure_fields': ['code',
                                                   'message',
                                                   'tool_result'],
                                'request_fields': ['name',
                                                   'arguments',
                                                   'instance_id',
                                                   'session_id',
                                                   'public_base_url',
                                                   'asserted_project_root']},
                   'workbench_api': {'transport': 'http',
                                     'socket': 'private Unix socket',
                                     'startup': {'module': 'APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.backend_process',
                                                 'arguments': ['--socket',
                                                               '<socket>',
                                                               '--project-root',
                                                               '<project-root>',
                                                               '--control-root',
                                                               '<control-root>',
                                                               '--instance-id',
                                                               '<instance-id>',
                                                               '--manifest-sha256',
                                                               '<manifest-sha256>',
                                                               '[--host-project-root '
                                                               '<host-project-root>]',
                                                               '[--default-workbench-storage '
                                                               '<disk|memory>]',
                                                               '[--default-journal-storage '
                                                               '<files|duckdb>]']},
                                     'routes': {'health': 'GET /health',
                                                'operation': 'POST '
                                                             '/workbench',
                                                'worker_runs': 'GET '
                                                               '/jobs/worker-runs'},
                                     'operations': ['workbench',
                                                    'lifecycle',
                                                    'release_command'],
                                     'request_fields': ['operation',
                                                        'name',
                                                        'arguments',
                                                        'instance_id',
                                                        'session_id']},
                   'previous_image_model_claim_selection': {'transport': 'cli',
                                                            'runner': 'docker',
                                                            'path': 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/native_model_selector.py',
                                                            'entrypoint': '/opt/venv/bin/python',
                                                            'arguments': ['/selector.py',
                                                                          '/model']}},
        'client': [{'component': 'C59', 'interface': 'database_api'},
                   {'component': 'C66', 'interface': 'worker_runs'}]},
 'state': {'reads': ['host settings',
                     'installed Tool registry',
                     'Project Manifest',
                     'Project Config',
                     'Project binding',
                     'Kernel results']}}
```

## Component Contract

### Run one read-only IWE Console query

#### Guarantee

Given a complete SQL string and valid result options, execute one read-only
query against the selected Project's IWE Console data. Treat the optional
cursor position as editor metadata.

Return result metadata with an inline page or a result file according to
the requested delivery mode and result format. Omit the SQL text from
the result. Reject invalid inputs and report query execution failures.

#### Tool API

Publish the enabled Tool names, descriptions, and schemas for an admitted
Project. Use the same registry to validate and dispatch named calls.
Return the Tool result or a failure for a stale registry, disabled Tool,
or invalid request.

For `POST /tools`, return HTTP 200 with the result when the operation succeeds.
Return HTTP 400 with a typed error for invalid request input. Return HTTP 500
with a typed, sanitized error for an internal fault that prevents handling the
request. An accepted input can still fail during operation. Do not classify
other failures as HTTP 400.

##### Formal Claim

This small claim checks only the three Tool API transport cases and the result
or typed-error response kind. It does not model message sanitization or the
complete response schema.

```lean
namespace WorkbenchToolApi

inductive Classification where
  | acceptedOperation
  | invalidRequestInput
  | internalFault
  deriving DecidableEq

inductive ResponseKind where
  | result
  | typedError
  deriving DecidableEq

def accepts (code : Nat) (classification : Classification)
    (kind : ResponseKind) : Bool :=
  match code, classification, kind with
  | 200, .acceptedOperation, .result => true
  | 400, .invalidRequestInput, .typedError => true
  | 500, .internalFault, .typedError => true
  | _, _, _ => false

example : accepts 200 .acceptedOperation .result = true := by decide
example : accepts 400 .invalidRequestInput .typedError = true := by decide
example : accepts 500 .internalFault .typedError = true := by decide
example : accepts 200 .acceptedOperation .typedError = false := by decide
example : accepts 400 .invalidRequestInput .result = false := by decide
example : accepts 400 .internalFault .typedError = false := by decide

end WorkbenchToolApi
```

#### Process boundary

Resolve the requested Project and return its Manifest pin and verified
host binding without opening DuckDB. Return its normalized Tool blacklist and
release workflow enablement.

Serve one admitted Project per Backend process over a private Unix
socket. Check the Project Manifest revision and instance identity before
readiness. Validate named IWE Console operations in the Backend and call
the Project's Kernel to execute queries and publish lifecycle updates.
When release workflows are enabled, revalidate the Project Manifest pin and
return the host command for the declared local or public Release entrypoint.

Use the Project Manifest's storage settings first, then the host
defaults. The caller owns the process lifetime and closes it when the
Project leaves the pool or the caller exits.

#### Shared host

The Backend coordinator reads the host settings, resolves explicit Project
roots, and publishes the compatible Tool catalog. It routes a named call
only to its selected Project. It holds a bounded pool of Project Backend
processes and closes them on eviction or shutdown.

MCP uses the private Unix socket for status, selection, catalog, and calls.
The configured host settings must remain current for Project calls.

#### References

AN-S-1456, AN-S-2566, AN-S-3059, and AN-T-2947.
