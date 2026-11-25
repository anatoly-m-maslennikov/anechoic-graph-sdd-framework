---
atom_family: SPEC
atom_id: AN-S-3069
container:
  component: C16
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 56
  updated_at: "2026-11-24T23:12:55.813309+00:00"
---
## Summary

Declare ADAPTERS

## Purpose

Provide guarded filesystem access, carrier I/O, and Journal storage.
Read validated Structure snapshots and check reviewed Model declarations.

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
            'state': 'local',
            'code': {
                'imports': {'only': ['metrics__shared.spec_rows', 'ADAPTERS_C30__shared.capture_native',
                                     'ADAPTERS_C30__shared.capture_indexed_lifecycle', 'ADAPTERS_C30__shared.native_carrier_hashes',
                                     'ADAPTERS_C30__shared.prepare_generation_snapshot',
                                     'ADAPTERS_C30__shared.capture_carrier_delta', 'ADAPTERS_C30__shared.capture_ticket_delta',
                                     'ADAPTERS_C30__shared.ReadContext', 'ADAPTERS_C30__shared.revalidate_native',
                                     'ADAPTERS_C30__shared.atomic_tempfile', 'ADAPTERS_C30__shared.TEMPORARY_DIRECTORY',
                                     'ADAPTERS_C30__shared.frontmatter_bounds', 'ADAPTERS_C30__shared.source_body']},
            },
            'io': {
                'server': {
                    'native_snapshot': {'transport': 'cli',
                     'runner': 'managed_python',
                     'module': 'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli',
                     'input_fields': ['root',
                                      'control_root',
                                      'manifest_path',
                                      'manifest_sha256',
                                      'project_prefix'],
                     'generation_input_fields': ['binding', 'endpoints'],
                     'admitted_carrier_delta': 'Read only addressed carriers when the caller supplies the Manifest pin.',
                     'output_fields': ['snapshot', 'stability_sha256', 'graph_config']},
                    'guarded_read': {
                        'transport': 'cli',
                        'runner': 'managed_python',
                        'path': 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__pub.py',
                        'arguments': ['--read-bounded', '<absolute-regular-file>'],
                        'response': 'up to 65536 bytes on stdout',
                    },
                },
            },
        },
    ),
)
```
