---
atom_family: SPEC
atom_id: AN-S-3069
container:
  component: C16
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 64
  updated_at: "2026-11-26T15:52:29.460570+00:00"
---
## Summary

Declare ADAPTERS

## Purpose

Provide guarded filesystem access, carrier I/O, and Journal storage.
Read validated Structure snapshots and check reviewed Model declarations.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C30',
    name='ADAPTERS',
    lens_whitelist=['SWD'],
)
```

## Component Boundaries

```python
{'state': 'local',
 'code': {'imports': {'only': ['metrics__shared.spec_rows',
                               'ADAPTERS_C30__shared.capture_native',
                               'ADAPTERS_C30__shared.capture_indexed_lifecycle',
                               'ADAPTERS_C30__shared.native_carrier_hashes',
                               'ADAPTERS_C30__shared.prepare_generation_snapshot',
                               'ADAPTERS_C30__shared.capture_carrier_delta',
                               'ADAPTERS_C30__shared.capture_ticket_delta',
                               'ADAPTERS_C30__shared.ReadContext',
                               'ADAPTERS_C30__shared.revalidate_native',
                               'ADAPTERS_C30__shared.atomic_tempfile',
                               'ADAPTERS_C30__shared.TEMPORARY_DIRECTORY',
                               'ADAPTERS_C30__shared.frontmatter_bounds',
                               'ADAPTERS_C30__shared.source_body',
                               'ADAPTERS_C30__shared.CarrierError',
                               'ADAPTERS_C30__shared.LimitReached',
                               'ADAPTERS_C30__shared.ReadFailure',
                               'ADAPTERS_C30__shared.SourceWatcher',
                               'ADAPTERS_C30__shared.TemporaryBoundaryError',
                               'ADAPTERS_C30__shared.append_record',
                               'ADAPTERS_C30__shared.append_sealed_events',
                               'ADAPTERS_C30__shared.attach_framework',
                               'ADAPTERS_C30__shared.configured_journal_root',
                               'ADAPTERS_C30__shared.journal_inbox',
                               'ADAPTERS_C30__shared.journal_storage',
                               'ADAPTERS_C30__shared.console_state_path',
                               'ADAPTERS_C30__shared.migrate_project_database',
                               'ADAPTERS_C30__shared.parse_carrier']},
          'exports': {'ADAPTERS_C30__shared.TEMPORARY_DIRECTORY': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__tests']},
                      'ADAPTERS_C30__shared.MAX_DATABASE_EVENT_BYTES': {'private': ['C59']},
                      'ADAPTERS_C30__shared.NativeCapture': 'public',
                      'ADAPTERS_C30__shared.NativeManifestChanged': 'public',
                      'ADAPTERS_C30__shared.SourceWatcher': {'private': ['C59',
                                                                         'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__tests']},
                      'ADAPTERS_C30__shared.UniqueSafeLoader': {'private': ['C59',
                                                                            'C61',
                                                                            'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/VALIDATE_ATOMS/validate_atoms_workers']},
                      'ADAPTERS_C30__shared.append_record': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__tests']},
                      'ADAPTERS_C30__shared.append_sealed_events': {'private': ['C59',
                                                                                'C71',
                                                                                'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__tests']},
                      'ADAPTERS_C30__shared.atom_identifier': {'private': ['C59']},
                      'ADAPTERS_C30__shared.CodeAccessOwnership': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'ADAPTERS_C30__shared.build_code_access_ownership': {'private': ['C59',
                                                                                       'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'ADAPTERS_C30__shared.canonical_json_bytes': {'private': ['C59']},
                      'ADAPTERS_C30__shared.check_native_manifest': 'public',
                      'ADAPTERS_C30__shared.check_yaml_resources': {'private': ['C59',
                                                                                'C61',
                                                                                'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/VALIDATE_ATOMS/validate_atoms_workers']},
                      'ADAPTERS_C30__shared.configured_journal_root': {'private': ['C59',
                                                                                   'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__tests']},
                      'ADAPTERS_C30__shared.content_record_span': {'private': ['C59']},
                      'ADAPTERS_C30__shared.emits_instance_inverse': {'private': ['C59']},
                      'ADAPTERS_C30__shared.journal_inbox': {'private': ['C59',
                                                                         'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__tests']},
                      'ADAPTERS_C30__shared.journal_storage': {'private': ['C59',
                                                                           'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__tests']},
                      'ADAPTERS_C30__shared.json_value': {'private': ['C59']},
                      'ADAPTERS_C30__shared.module_visibility': {'private': ['C59']},
                      'ADAPTERS_C30__shared.native_header_view': 'public',
                      'ADAPTERS_C30__shared.parse_component_manifest_fields': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'ADAPTERS_C30__shared.parse_component_manifest': {'private': ['C59',
                                                                                    'C74',
                                                                                    'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'ADAPTERS_C30__shared.pending_database_journal': {'private': ['C59']},
                      'ADAPTERS_C30__shared.read_component_contract': {'private': ['C59']},
                      'ADAPTERS_C30__shared.read_component_seed_manifest': {'private': ['C59']},
                      'ADAPTERS_C30__shared.validated_journal_root': {'private': ['C59']},
                      'ADAPTERS_C30__shared.value_excluding_declared_children': {'private': ['C59']},
                      'ADAPTERS_C30__shared.CarrierError': 'public',
                      'ADAPTERS_C30__shared.ParsedCarrier': 'public',
                      'ADAPTERS_C30__shared.parse_carrier': 'public',
                      'ADAPTERS_C30__shared.content_key': 'public',
                      'ADAPTERS_C30__shared.content_lines': 'public',
                      'ADAPTERS_C30__shared.direct_markdown': 'public',
                      'ADAPTERS_C30__shared.formal_claim_fences': 'public',
                      'ADAPTERS_C30__shared.parse_content': 'public',
                      'ADAPTERS_C30__shared.unfenced_atx_headings': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH',
                                                                                 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/VALIDATE_ATOMS/validate_atoms_workers']},
                      'ADAPTERS_C30__shared.section_markdown': 'public',
                      'ADAPTERS_C30__shared.source_markdown': 'public',
                      'ADAPTERS_C30__shared.capture_native': 'public',
                      'ADAPTERS_C30__shared.capture_indexed_lifecycle': {'private': ['C16',
                                                                                     'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__tests']},
                      'ADAPTERS_C30__shared.attach_framework': {'shared': ['C59',
                                                                           'C71',
                                                                           'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__tests']},
                      'ADAPTERS_C30__shared.console_state_path': {'shared': ['C59',
                                                                            'C68',
                                                                            'C71',
                                                                            'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__tests']},
                      'project_database__pub.console_state_path': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_CODEX']},
                      'ADAPTERS_C30__shared.migrate_project_database': {'shared': ['C59',
                                                                                   'C71',
                                                                                   'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__tests']},
                      'ADAPTERS_C30__shared.mark_startup_timing': {'private': ['C75', 'C68',
                                                                               'C69',
                                                                               'CS1']},
                      'ADAPTERS_C30__shared.native_carrier_hashes': {'shared': ['C69',
                                                                                'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__tests']},
                      'ADAPTERS_C30__shared.prepare_generation_snapshot': {'shared': ['C69',
                                                                                      'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__tests']},
                      'ADAPTERS_C30__shared.capture_ticket_delta': {'shared': ['C69',
                                                                               'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__tests']},
                      'ADAPTERS_C30__shared.capture_carrier_delta': {'shared': ['C69',
                                                                                'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__tests']},
                      'ADAPTERS_C30__shared.NativeSnapshotChanged': {'private': ['C69']},
                      'ADAPTERS_C30__shared.UnrepresentableCarrierDelta': {'private': ['C69',
                                                                                       'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests']},
                      'ADAPTERS_C30__shared.read_structure': 'public',
                      'ADAPTERS_C30__shared.StructureSnapshot': 'public',
                      'topic_dependencies__pub.validate_dependencies_claim': 'public',
                      'topic_dependencies__pub.DEPENDENCIES_CHECK_SOURCE_SHA256': 'public',
                      'ADAPTERS_C30__shared.read_current_carriers': 'public',
                      'ADAPTERS_C30__shared.read_current_model_carriers': 'public',
                      'relation_declaration_catalog__pub.build_relation_declaration_catalog': 'public',
                      'ADAPTERS_C30__shared.active_manifest_carriers': 'public',
                      'ADAPTERS_C30__shared.select_manifest_carriers': 'public',
                      'ADAPTERS_C30__shared.manifest_inputs': 'public',
                      'ADAPTERS_C30__shared.manifest_sources': 'public',
                      'ADAPTERS_C30__shared.manifest_state_fields': 'public',
                      'ADAPTERS_C30__shared.atomic_tempfile': 'public',
                      'ADAPTERS_C30__shared.owned_temporary_root': 'public',
                      'source_watcher__pub.SourceWatcher': 'public',
                      'cardinality__pub.cardinality_bounds': 'public',
                      'dataclass_field_contract__pub.has_dataclass_field_contracts': 'public',
                      'dataclass_field_contract__pub.validate_field_contracts': 'public',
                      'ADAPTERS_C30__shared.canonical_model_address': 'public',
                      'ADAPTERS_C30__shared.model_declaration_subject': 'public',
                      'ADAPTERS_C30__shared.simple_model_address': 'public',
                      'placement_claim__pub.parse_placement_claim': 'public',
                      'placement_claim__pub.parse_placement_rules': 'public',
                      'ADAPTERS_C30__shared.bind_ordering_declarations': 'public',
                      'ADAPTERS_C30__shared.order_properties': 'public',
                      'ADAPTERS_C30__shared.frontmatter_bounds': 'public',
                      'ADAPTERS_C30__shared.source_body': 'public',
                      'content_records__pub.content_record_span': 'public',
                      'content_records__pub.records_by_path': 'public',
                      'content_records__pub.value_excluding_declared_children': 'public',
                      'markdown_content__pub.parse_content': {'private': ['C45']},
                      'ADAPTERS_C30__shared.CURRENT_STATUSES': 'public',
                      'ADAPTERS_C30__shared.revalidate_native': 'public',
                      'source_row__pub.atom': 'public',
                      'source_row__pub.canonical': 'public',
                      'ADAPTERS_C30__shared.canonical': 'public',
                      'ADAPTERS_C30__shared.records_by_path': 'public',
                      'ADAPTERS_C30__shared.ProjectSelectionError': 'public',
                      'ADAPTERS_C30__shared.bound_selection': {'private': ['C16',
                                                                           'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                           'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE']},
                      'source_row__pub.canonical_row': 'public',
                      'source_row__pub.json_value': 'public',
                      'code_access_rules__pub.module_visibility': 'public',
                      'code_access_rules__pub.parse_code_access': 'public',
                      'component_manifest__pub.parse_component_manifest': 'public',
                      'component_manifest__pub.parse_component_manifest_fields': 'public',
                      'ADAPTERS_C30__shared.formal_claim': 'public',
                      'ADAPTERS_C30__shared.iter_formal_claims': 'public',
                      'ADAPTERS_C30__shared.bindings_from_workbench_rows': 'public',
                      'ADAPTERS_C30__shared.class_bindings': 'public',
                      'ADAPTERS_C30__shared.NativeModelClaimError': 'public',
                      'ADAPTERS_C30__shared.parse_native_model_claim': 'public',
                      'ADAPTERS_C30__shared.validate_aspect_hierarchy': 'public',
                      'ADAPTERS_C30__shared.validate_aspect_instance': 'public',
                      'component_seed_manifest__pub.read_component_seed_manifest': 'public',
                      'realization_ownership__pub.CodeAccessOwnership': 'public',
                      'realization_ownership__pub.build_code_access_ownership': 'public',
                      'ADAPTERS_C30__shared.parse_structure': {'shared': ['C16',
                                                                          'C59',
                                                                          'C61']},
                      'ADAPTERS_C30__shared.realization_component_paths': {'shared': ['C59',
                                                                                      'C61']},
                      'ADAPTERS_C30__shared.ScopeUnitDeclaration': 'public',
                      'ADAPTERS_C30__shared.parse_scope_unit_declaration': 'public',
                      'ADAPTERS_C30__shared.ScopeUnitDeclarations': 'public',
                      'ADAPTERS_C30__shared.read_scope_unit_declarations': 'public',
                      'ADAPTERS_C30__shared.is_current_requirement_declaration': 'public',
                      'ADAPTERS_C30__shared.matches_carrier_label': 'public',
                      'legacy_relation__pub.emits_instance_inverse': 'public',
                      'ADAPTERS_C30__shared.model_class_target': 'public',
                      'ADAPTERS_C30__shared.PythonModelClaimError': 'public',
                      'ADAPTERS_C30__shared.parse_grouped_python_model_claim': 'public',
                      'ADAPTERS_C30__shared.parse_python_model_claim': 'public',
                      'ADAPTERS_C30__shared.parse_structured_python_model_claim': 'public',
                      'ADAPTERS_C30__shared.ProjectSettingsValueError': 'public',
                      'ADAPTERS_C30__shared.bind_settings_selection': {'private': ['C16']},
                      'ADAPTERS_C30__shared.control_root': 'public',
                      'ADAPTERS_C30__shared.project_identity': 'public',
                      'ADAPTERS_C30__shared.project_identity_prefix': 'public',
                      'component_contract__pub.read_component_contract': 'public',
                      'ADAPTERS_C30__shared.DELEGATION_ROLE_FOLDERS': 'public',
                      'ADAPTERS_C30__shared.ScopeDeclarationError': 'public',
                      'ADAPTERS_C30__shared.has_projection_marker': 'public',
                      'ADAPTERS_C30__shared.has_scope_declaration_form': 'public',
                      'ADAPTERS_C30__shared.read_scope_carrier': 'public',
                      'ADAPTERS_C30__shared.Span': 'public',
                      'ADAPTERS_C30__shared.Name': 'public',
                      'ADAPTERS_C30__shared.ValueLiteral': 'public',
                      'ADAPTERS_C30__shared.FormatReference': 'public',
                      'ADAPTERS_C30__shared.Cardinality': 'public',
                      'ADAPTERS_C30__shared.Qualification': 'public',
                      'ADAPTERS_C30__shared.DeclaredReference': 'public',
                      'ADAPTERS_C30__shared.SelectionGroup': 'public',
                      'ADAPTERS_C30__shared.SelectionSuffix': 'public',
                      'ADAPTERS_C30__shared.PathStep': 'public',
                      'ADAPTERS_C30__shared.Path': 'public',
                      'ADAPTERS_C30__shared.RelationLink': 'public',
                      'ADAPTERS_C30__shared.RelationChain': 'public',
                      'ADAPTERS_C30__shared.ParsedSubject': 'public',
                      'ADAPTERS_C30__shared.parse_subject_expression': 'public',
                      'ADAPTERS_C30__shared.render_subject': 'public',
                      'ADAPTERS_C30__shared.GrammarSource': 'public',
                      'ADAPTERS_C30__shared.GrammarPin': 'public',
                      'ADAPTERS_C30__shared.InitialAtomSelector': 'public',
                      'ADAPTERS_C30__shared.SubjectNotationError': 'public',
                      'ADAPTERS_C30__shared.SubjectProfile': 'public',
                      'ADAPTERS_C30__shared.get_profile': 'public',
                      'ADAPTERS_C30__shared.namespace_local_expression': 'public',
                      'ADAPTERS_C30__shared.parse_initial_atom_selector': 'public',
                      'ADAPTERS_C30__shared.parse_subject': 'public',
                      'ADAPTERS_C30__shared.profile_evidence': 'public',
                      'ADAPTERS_C30__shared.StatusModelError': 'public',
                      'ADAPTERS_C30__shared.canonical_status': 'public',
                      'ADAPTERS_C30__shared.is_logical_container': 'public',
                      'ADAPTERS_C30__shared.project_root_container_view': 'public',
                      'ADAPTERS_C30__shared.PlacementError': 'public',
                      'ADAPTERS_C30__shared.admitted_parent': 'public',
                      'ADAPTERS_C30__shared.carrier_slug': 'public',
                      'ADAPTERS_C30__shared.compile_role_folders': 'public',
                      'ADAPTERS_C30__shared.derive_filename': 'public',
                      'ADAPTERS_C30__shared.role_folders_from_orders': 'public',
                      'carrier_read__pub.CarrierError': 'public',
                      'carrier_read__pub.ParsedCarrier': 'public',
                      'carrier_read__pub.parse_carrier': 'public',
                      'ADAPTERS_C30__shared.canonical_native_header': 'public',
                      'ADAPTERS_C30__shared.native_header_model_fields': 'public',
                      'native_carrier_header__pub.native_header_view': 'public',
                      'ADAPTERS_C30__shared.ARCHIVE_DIRECTORY': 'public',
                      'ADAPTERS_C30__shared.COMPLETE_DIRECTORY': 'public',
                      'ADAPTERS_C30__shared.CUSTOM_MODEL_DIRECTORY': 'public',
                      'ADAPTERS_C30__shared.DRAFT_DIRECTORY': 'public',
                      'ADAPTERS_C30__shared.PROJECT_CONFIG_DIRECTORY': 'public',
                      'ADAPTERS_C30__shared.active_spec_directories': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE',
                                                                                   'C19']},
                      'ADAPTERS_C30__shared.spec_folder_layout': {'private': ['C16', 'C93']},
                      'lens_scopes__pub.compile_lens_groups': {'shared': ['C93']},
                      'lens_scopes__pub.validate_lens_whitelist': {'shared': ['C93']},
                      'project_manifest__pub.manifest_summary_fields': {'shared': ['C93']},
                      'ADAPTERS_C30__shared.READY_DIRECTORY': 'public',
                      'ADAPTERS_C30__shared.TICKET_DIRECTORY': 'public',
                      'ADAPTERS_C30__shared.native_carrier_path': 'public',
                      'ADAPTERS_C30__shared.project_goal_filename': 'public',
                      'ADAPTERS_C30__shared.native_ticket_asset': 'public',
                      'ADAPTERS_C30__shared.native_ticket_label': 'public',
                      'ADAPTERS_C30__shared.spec_lens_directories': 'public',
                      'atom_reference__pub.atom_identifier': 'public',
                      'atom_reference__pub.derive_atom_ref': 'public',
                      'spec_file_reader.read_spec_file': {'shared': ['C95']},
                      'ADAPTERS_C30__shared.GROUP_FIELDS': 'public',
                      'ADAPTERS_C30__shared.GROUP_ORDER': 'public',
                      'ADAPTERS_C30__shared.ROLE_FIELDS': 'public',
                      'ADAPTERS_C30__shared.canonical_role_name': 'public',
                      'ADAPTERS_C30__shared.carrier_read_view': 'public',
                      'ADAPTERS_C30__shared.carrier_status_folder': 'public',
                      'ADAPTERS_C30__shared.equal_values': 'public',
                      'ADAPTERS_C30__shared.header_field_paths': 'public',
                      'ADAPTERS_C30__shared.header_path': 'public',
                      'ADAPTERS_C30__shared.header_value': 'public',
                      'ADAPTERS_C30__shared.matches_named_value': 'public',
                      'ADAPTERS_C30__shared.named_value_token': 'public',
                      'ADAPTERS_C30__shared.path_value': 'public',
                      'ADAPTERS_C30__shared.CEILINGS': 'public',
                      'ADAPTERS_C30__shared.LimitReached': 'public',
                      'ADAPTERS_C30__shared.ReadContext': 'public',
                      'ADAPTERS_C30__shared.ReadFailure': 'public',
                      'ADAPTERS_C30__shared.open_regular': 'public',
                      'ADAPTERS_C30__shared.protected': 'public',
                      'ADAPTERS_C30__shared.TemporaryBoundaryError': 'public',
                      'ADAPTERS_C30__shared.validate_directory_components': 'public',
                      'ADAPTERS_C30__shared.parse_settings_carrier': 'public',
                      'ADAPTERS_C30__shared.read_settings_carrier': 'public',
                      'ADAPTERS_C30__shared.write_settings_carrier': 'public',
                      'carrier_syntax__pub.CarrierError': 'public',
                      'carrier_syntax__pub.UniqueSafeLoader': 'public',
                      'carrier_syntax__pub.check_yaml_resources': 'public',
                      'carrier_syntax__pub.parse_carrier_syntax': 'public',
                      'journal_settings__pub.configured_journal_root': 'public',
                      'journal_settings__pub.journal_storage': 'public',
                      'journal_settings__pub.validated_journal_root': 'public',
                      'work_journal__pub.MAX_DATABASE_EVENT_BYTES': 'public',
                      'work_journal__pub.PROJECT_DATABASE': 'public',
                      'work_journal__pub.append_sealed_events': 'public',
                      'work_journal__pub.canonical_json_bytes': 'public',
                      'work_journal__pub.journal_inbox': 'public',
                      'work_journal__pub.pending_database_journal': 'public'}},
 'io': {'server': {'native_snapshot': {'transport': 'cli',
                                       'runner': 'managed_python',
                                       'module': 'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli',
                                       'input_fields': ['root',
                                                        'control_root',
                                                        'manifest_path',
                                                        'manifest_sha256',
                                                        'project_prefix'],
                                       'generation_input_fields': ['binding',
                                                                   'endpoints'],
                                       'admitted_carrier_delta': 'Read '
                                                                 'only '
                                                                 'addressed '
                                                                 'carriers '
                                                                 'when '
                                                                 'the '
                                                                 'caller '
                                                                 'supplies '
                                                                 'the '
                                                                 'Manifest '
                                                                 'pin.',
                                       'output_fields': ['snapshot',
                                                         'stability_sha256',
                                                         'graph_config']},
                   'guarded_read': {'transport': 'cli',
                                    'runner': 'managed_python',
                                    'path': 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__pub.py',
                                    'arguments': ['--read-bounded',
                                                  '<absolute-regular-file>'],
                                    'response': 'up to 65536 bytes on '
                                                'stdout'}}}}
```

## Component Contract

### Read guarded filesystem inputs

#### Guarantee

Open admitted filesystem paths without following symbolic links. A bounded read checks its declared roots and read limits, refuses protected paths, and records input fingerprints. A caller can check whether its recorded inputs still match the filesystem.

Parse UTF-8 YAML frontmatter within fixed syntax limits. Refuse aliases,
merge keys, duplicate keys, and non-string mapping keys. Return header
data and body text for the caller to interpret.

Read and write TOML settings carriers. Validate a replacement before
publishing it.

Append Journal rows to Project-local files in input order or stage them
for the database owner. Return receipts for completed appends. Report
partial completion when a batch stops.

Read grouped and historical Header fields without altering the carrier.
Reject conflicting aliases. Read legacy Atom identifiers. Given an admitted Atom ID, version, and
Status, return its exact reference in the form `<atom-id>@<version>`.
Append `-draft` for Draft. This operation has no file effects.

Read native Headers and derive Carrier filenames and directories from
the supplied fields. Preserve the legacy filename grammar and reject
unsupported paths or contradictory fields.

Read authored Component Contracts and recognize legacy Scope Unit carriers.
Parse and render Subject notation with the selected grammar profile.

Read the legacy Project Settings selected for the current request.
Parse legacy Python Claims as literal calls and preserve their
Model or Instance grouping.

Read native Model Claims and Structure declarations without executing them.
Check Dependencies Declarations against the reviewed callback source.
Read one published Structure snapshot into a read-only value. Refuse
malformed JSON and invalid Component or Package records.
Map realization paths to declared Component and Package owners. Retain
the source pins when discovering legacy Scope Unit declarations.

Capture Project carriers with their revisions, containment and source pins.
Report invalid sources and refuse a capture if the Manifest or carrier
inventory changes during the read. Decode Markdown headings and retain
the source ranges for declared Content properties.

Read literal placement rules, property order, and dataclass field contracts
from Model Claims. Decode cardinality bounds and normalize Model addresses.

Read and decode active Project Manifest carriers from guarded inputs.
Allocate temporary files under the selected Project on the destination
filesystem. Observe changes in selected directories and return their
old and new paths to the caller.

Index Relation Declarations and their inverse names. Refuse duplicate
names, unresolved derivations, and Relations that derive from themselves.

Read Current legacy carriers with their exact source bytes and pins.
Select Model Declarations and verify any explicit Draft overlay against
its predecessor and revision pins.

#### Claim

##### Formal Claim

The following Lean claim covers only `frontmatter_bounds` and `source_body`
in `carrier_body__pub.py`. Each `Nat` in an input list denotes one byte
(0 through 255). `missingDelimiter` represents no bounds or the explicit
unsupported-delimiter error; the `path` supplied to `source_body` is used
for the error message. It is not read as a file.

```lean
import Lean

namespace CarrierBodyContract

-- Byte offsets are zero-based; the separator belongs to the closing boundary.
def openingEnd (raw : List Nat) : Option Nat :=
  if raw.take 4 == [45,45,45,10] then some 4
  else if raw.take 5 == [45,45,45,13,10] then some 5
  else none

-- A closing line is exactly three hyphens with an LF or CRLF terminator.
def closingEnd (raw : List Nat) (separator : Nat) : Option Nat := do
  let afterSep ← if (raw.drop separator).take 2 == [13,10] then some (separator + 2)
    else if (raw.drop separator).take 1 == [10] then some (separator + 1)
    else none
  if (raw.drop afterSep).take 3 != [45,45,45] then none
  else if (raw.drop (afterSep + 3)).take 2 == [13,10] then some (afterSep + 5)
  else if (raw.drop (afterSep + 3)).take 1 == [10] then some (afterSep + 4)
  else none

def bounds (raw : List Nat) : Option (Nat × Nat × Nat) := do
  let opening ← openingEnd raw
  let start ← ((List.range raw.length).drop (opening - 1)).find? (fun i => (closingEnd raw i).isSome)
  let stop ← closingEnd raw start
  some (opening, start, stop)

inductive Outcome where
  | missingDelimiter
  | body (bytes : List Nat)
  deriving Repr, BEq, DecidableEq

def body (raw : List Nat) : Outcome :=
  match bounds raw with
  | none => .missingDelimiter
  | some (_, _, stop) => .body (raw.drop stop)

-- Project-level effect guarantee: these operations make no Project state changes,
-- filesystem accesses, or network accesses. This is an implementation obligation;
-- the pure definitions above do not establish it for the Python implementation.
end CarrierBodyContract
```

#### References

AN-S-3069 and AN-T-2944.
