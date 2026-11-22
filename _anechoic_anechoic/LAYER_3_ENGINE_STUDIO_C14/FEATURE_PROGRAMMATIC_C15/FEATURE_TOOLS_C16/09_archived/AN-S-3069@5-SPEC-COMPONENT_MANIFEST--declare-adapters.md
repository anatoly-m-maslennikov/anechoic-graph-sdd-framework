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
  version: 5
  updated_at: "2026-11-22T02:36:17.966050+00:00"
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
