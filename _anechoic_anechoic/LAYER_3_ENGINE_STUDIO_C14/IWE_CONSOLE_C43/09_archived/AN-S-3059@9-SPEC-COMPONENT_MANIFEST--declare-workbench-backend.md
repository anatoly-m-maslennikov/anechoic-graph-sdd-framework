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
  version: 9
  updated_at: "2026-11-22T02:28:07.870773+00:00"
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
                    'C53',
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
                    'previous_image_model_claim_selection': {
                        'transport': 'cli',
                        'runner': 'docker',
                        'path': 'LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/native_model_selector.py',
                        'entrypoint': '/opt/venv/bin/python',
                        'arguments': ['/selector.py', '/model'],
                    },
                },
            },
        },
    ),
)
```
