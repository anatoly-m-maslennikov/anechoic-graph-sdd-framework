---
atom_family: SPEC
atom_id: AN-S-3056
container:
  component: C15
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 13
  updated_at: "2026-11-22T03:15:21.002362+00:00"
---

## Summary

Declare TOOLS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C16',
        name='TOOLS',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
        boundaries={
            'code': {
                'imports': [
                    'formal_claim__pub.formal_claim',
                    'formal_claim__pub.iter_formal_claims',
                    'model_catalog__pub.bindings_from_workbench_rows',
                    'native_model_claim__pub.NativeModelClaimError',
                    'native_model_claim__pub.parse_native_model_claim',
                    'native_model_claim__pub.validate_aspect_hierarchy',
                    'native_model_claim__pub.validate_aspect_instance',
                    'realization_ownership__pub.build_code_access_ownership',
                    'scope_declaration_parse__pub.ScopeUnitDeclaration',
                    'scope_declaration_parse__pub.parse_scope_unit_declaration',
                    'scope_unit_declarations__pub.ScopeUnitDeclarations',
                    'scope_unit_declarations__pub.read_scope_unit_declarations',
                    'carrier_compat__pub.is_current_requirement_declaration',
                    'legacy_relation__pub.emits_instance_inverse',
                    'model_class_subject__pub.model_class_target',
                    'python_claim__pub.PythonModelClaimError',
                    'python_claim__pub.parse_python_model_claim',
                    'python_claim__pub.parse_structured_python_model_claim',
                    'settings_context__pub.bind_settings_selection',
                    'settings_context__pub.bound_selection',
                    'component_contract__pub.read_component_contract',
                    'scope_carrier__pub.DELEGATION_ROLE_FOLDERS',
                    'scope_carrier__pub.ScopeDeclarationError',
                    'scope_carrier__pub.has_projection_marker',
                    'scope_carrier__pub.has_scope_declaration_form',
                    'scope_carrier__pub.read_scope_carrier',
                    'subject_notation__pub',
                    'subject_notation__pub.Name',
                    'subject_notation__pub.Path',
                    'subject_notation__pub.Qualification',
                    'subject_notation__pub.RelationChain',
                    'subject_notation__pub.SelectionGroup',
                    'subject_notation__pub.SelectionSuffix',
                    'subject_notation__pub.SubjectNotationError',
                    'subject_notation__pub.get_profile',
                    'subject_notation__pub.namespace_local_expression',
                    'subject_notation__pub.parse_subject_expression',
                    'subject_notation__pub.render_subject',
                    'carrier_compat__pub.StatusModelError',
                    'carrier_compat__pub.project_root_container_view',
                    'carrier_layout__pub.PlacementError',
                    'carrier_layout__pub.admitted_parent',
                    'carrier_layout__pub.carrier_slug',
                    'carrier_layout__pub.derive_filename',
                    'carrier_layout__pub.role_folders_from_orders',
                    'carrier_read__pub.CarrierError',
                    'carrier_read__pub.ParsedCarrier',
                    'carrier_read__pub.parse_carrier',
                    'native_carrier_header__pub.canonical_native_header',
                    'native_carrier_header__pub.native_header_model_fields',
                    'native_carrier_header__pub.native_header_view',
                    'native_carrier_placement__pub.ARCHIVE_DIRECTORY',
                    'native_carrier_placement__pub.COMPLETE_DIRECTORY',
                    'native_carrier_placement__pub.DRAFT_DIRECTORY',
                    'native_carrier_placement__pub.PROJECT_CONFIG_DIRECTORY',
                    'native_carrier_placement__pub.READY_DIRECTORY',
                    'native_carrier_placement__pub.TICKET_DIRECTORY',
                    'native_carrier_placement__pub.native_carrier_path',
                    'native_carrier_placement__pub.native_ticket_asset',
                    'native_carrier_placement__pub.native_ticket_label',
                    'native_carrier_placement__pub.spec_lens_directories',
                    'atom_reference__pub.atom_identifier',
                    'atom_reference__pub.derive_atom_ref',
                    'carrier_compat__pub.GROUP_FIELDS',
                    'carrier_compat__pub.GROUP_ORDER',
                    'carrier_compat__pub.ROLE_FIELDS',
                    'carrier_compat__pub.canonical_role_name',
                    'carrier_compat__pub.carrier_read_view',
                    'carrier_compat__pub.carrier_status_folder',
                    'carrier_compat__pub.equal_values',
                    'carrier_compat__pub.header_field_paths',
                    'carrier_compat__pub.header_path',
                    'carrier_compat__pub.header_value',
                    'carrier_compat__pub.matches_named_value',
                    'carrier_compat__pub.named_value_token',
                    'carrier_compat__pub.path_value',
                    'ADAPTERS_C30__pub.TemporaryBoundaryError',
                    'ADAPTERS_C30__pub.validate_directory_components',
                    'settings_carrier__pub.parse_settings_carrier',
                    'settings_carrier__pub.read_settings_carrier',
                    'FEATURE_PROGRAMMATIC__shared.Atom',
                    'FEATURE_PROGRAMMATIC__shared.DEPENDENCIES_CLAIM_SHA256',
                    'FEATURE_PROGRAMMATIC__shared.dependencies_are_distinct',
                    'FEATURE_PROGRAMMATIC__shared.has_dataclass_field_contracts',
                    'FEATURE_PROGRAMMATIC__shared.validate_dependencies_claim',
                    'FEATURE_PROGRAMMATIC__shared.verify_packaged_dependencies_check',
                    'import_graph__shared.capture',
                    'import_graph__shared.code_access_occurrences',
                    'FEATURE_MODEL_VALIDATION__shared.check_code_access',
                ],
                'exports': {
                    'FEATURE_TOOLS__shared': None,
                    'FEATURE_TOOLS__shared.atomic_tempfile': None,
                    'FEATURE_TOOLS__shared.bind_native_runtime': None,
                    'FEATURE_TOOLS__shared.owned_temporary_root': None,
                    'FEATURE_TOOLS__pub': 'public',
                    'FEATURE_TOOLS__pub.FailureRecord': 'public',
                    'FEATURE_TOOLS__pub.ExplicitBlockingRuntimeFailure': 'public',
                    'FEATURE_TOOLS__pub.operation_error_boundary': 'public',
                    'FEATURE_TOOLS__pub.report_failure': 'public',
                    'FEATURE_TOOLS__pub.run_process': 'public',
                    'FEATURE_TOOLS__pub.ManifestIdentity': 'public',
                    'FEATURE_TOOLS__pub.NativeProjectSelection': 'public',
                    'FEATURE_TOOLS__pub.ProjectSelection': 'public',
                    'FEATURE_TOOLS__pub.ProjectSelectionError': 'public',
                    'FEATURE_TOOLS__pub.declared_release_entrypoint': {'private': ['LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP']},
                    'FEATURE_TOOLS__pub.discover_native_project': 'public',
                    'FEATURE_TOOLS__pub.LIFECYCLE_TOOLS': {'private': ['LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP']},
                    'FEATURE_TOOLS__pub.bind_native_runtime': {'private': ['LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP']},
                    'FEATURE_TOOLS__pub.execute_native_lifecycle': {'private': ['LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP']},
                    'FEATURE_TOOLS__pub.is_native_control_name': 'public',
                    'FEATURE_TOOLS__pub.mcp_tool_blacklist': 'public',
                    'FEATURE_TOOLS__pub.rebind_native_selection': 'public',
                    'FEATURE_TOOLS__pub.resolve_native_project': 'public',
                },
            },
        },
    ),
)
```
