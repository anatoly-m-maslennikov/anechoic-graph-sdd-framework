---
atom_family: SPEC
atom_id: AN-S-3069
container:
  component: C16
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 6
  updated_at: "2026-11-22T02:43:39.333595+00:00"
---

## Summary

Declare ADAPTERS

## Purpose

Provide guarded filesystem access, carrier I/O, and Journal storage.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C30',
        name='ADAPTERS',
        lens_whitelist=['SWD'],
        boundaries={
            'code': {
                'imports': {'only': []},
                'exports': {
                    'carrier_compat__pub.StatusModelError': 'public',
                    'carrier_compat__pub.canonical_status': 'public',
                    'carrier_compat__pub.is_logical_container': 'public',
                    'carrier_compat__pub.project_root_container_view': 'public',
                    'carrier_layout__pub.PlacementError': 'public',
                    'carrier_layout__pub.admitted_parent': 'public',
                    'carrier_layout__pub.carrier_slug': 'public',
                    'carrier_layout__pub.compile_role_folders': 'public',
                    'carrier_layout__pub.derive_filename': 'public',
                    'carrier_layout__pub.role_folders_from_orders': 'public',
                    'carrier_read__pub.CarrierError': 'public',
                    'carrier_read__pub.ParsedCarrier': 'public',
                    'carrier_read__pub.parse_carrier': 'public',
                    'native_carrier_header__pub.canonical_native_header': 'public',
                    'native_carrier_header__pub.native_header_model_fields': 'public',
                    'native_carrier_header__pub.native_header_view': 'public',
                    'native_carrier_placement__pub.ARCHIVE_DIRECTORY': 'public',
                    'native_carrier_placement__pub.COMPLETE_DIRECTORY': 'public',
                    'native_carrier_placement__pub.CUSTOM_MODEL_DIRECTORY': 'public',
                    'native_carrier_placement__pub.DRAFT_DIRECTORY': 'public',
                    'native_carrier_placement__pub.PROJECT_CONFIG_DIRECTORY': 'public',
                    'native_carrier_placement__pub.READY_DIRECTORY': 'public',
                    'native_carrier_placement__pub.TICKET_DIRECTORY': 'public',
                    'native_carrier_placement__pub.native_carrier_path': 'public',
                    'native_carrier_placement__pub.native_ticket_asset': 'public',
                    'native_carrier_placement__pub.native_ticket_label': 'public',
                    'native_carrier_placement__pub.spec_lens_directories': 'public',
                    'atom_reference__pub.atom_identifier': 'public',
                    'atom_reference__pub.derive_atom_ref': 'public',
                    'carrier_compat__pub.GROUP_FIELDS': 'public',
                    'carrier_compat__pub.GROUP_ORDER': 'public',
                    'carrier_compat__pub.ROLE_FIELDS': 'public',
                    'carrier_compat__pub.canonical_role_name': 'public',
                    'carrier_compat__pub.carrier_read_view': 'public',
                    'carrier_compat__pub.carrier_status_folder': 'public',
                    'carrier_compat__pub.equal_values': 'public',
                    'carrier_compat__pub.header_field_paths': 'public',
                    'carrier_compat__pub.header_path': 'public',
                    'carrier_compat__pub.header_value': 'public',
                    'carrier_compat__pub.matches_named_value': 'public',
                    'carrier_compat__pub.named_value_token': 'public',
                    'carrier_compat__pub.path_value': 'public',
                    'ADAPTERS_C30__pub.CEILINGS': 'public',
                    'ADAPTERS_C30__pub.LimitReached': 'public',
                    'ADAPTERS_C30__pub.ReadContext': 'public',
                    'ADAPTERS_C30__pub.ReadFailure': 'public',
                    'ADAPTERS_C30__pub.open_regular': 'public',
                    'ADAPTERS_C30__pub.protected': 'public',
                    'ADAPTERS_C30__pub.TemporaryBoundaryError': 'public',
                    'ADAPTERS_C30__pub.validate_directory_components': 'public',
                    'settings_carrier__pub.parse_settings_carrier': 'public',
                    'settings_carrier__pub.read_settings_carrier': 'public',
                    'settings_carrier__pub.write_settings_carrier': 'public',
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
                    'work_journal__pub.pending_database_journal': 'public',
                },
            },
        },
    ),
)
```
