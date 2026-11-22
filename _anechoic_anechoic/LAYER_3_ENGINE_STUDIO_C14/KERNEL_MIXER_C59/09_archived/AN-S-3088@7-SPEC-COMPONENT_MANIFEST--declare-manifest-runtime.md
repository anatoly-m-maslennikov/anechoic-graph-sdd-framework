---
atom_family: SPEC
atom_id: AN-S-3088
container:
  component: C59
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 7
  updated_at: "2026-11-22T03:15:21.487187+00:00"
---

## Summary

Declare Manifest Runtime

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C62',
        name='Manifest Runtime',
        lens_whitelist=['SPEC'],
        boundaries={
            'code': {
                'imports': [
                    'code_access_rules__pub.parse_code_access',
                    'component_manifest__pub.parse_component_manifest_fields',
                    'package_spec__pub.read_package_spec',
                    'subject_notation__pub',
                    'carrier_read__pub.parse_carrier',
                    'native_carrier_header__pub.native_header_view',
                    'native_carrier_placement__pub.ARCHIVE_DIRECTORY',
                    'native_carrier_placement__pub.CUSTOM_MODEL_DIRECTORY',
                    'native_carrier_placement__pub.DRAFT_DIRECTORY',
                    'native_carrier_placement__pub.PROJECT_CONFIG_DIRECTORY',
                    'native_carrier_placement__pub.READY_DIRECTORY',
                    'atom_reference__pub.derive_atom_ref',
                ],
                'exports': {
                    'MANIFEST_RUNTIME_C62__shared.run_manifest_runtime': {
                        'private': ['LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP'],
                    },
                },
            },
            'io': {
                'server': {
                    'image_model_compile': {
                        'transport': 'cli',
                        'runner': 'managed_python',
                        'module': 'LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.image_model_compile',
                    },
                },
            },
        },
    ),
)
```
