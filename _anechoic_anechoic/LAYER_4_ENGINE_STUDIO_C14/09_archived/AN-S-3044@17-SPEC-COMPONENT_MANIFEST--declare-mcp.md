---
atom_family: SPEC
atom_id: AN-S-3044
container:
  component: C14
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 17
  updated_at: "2026-11-22T06:47:25.011357+00:00"
---

## Summary

Declare MCP

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C21',
        name='MCP',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'code': {
                'imports': {'only': [
                    'native_source_rows__pub.capture_native',
                    'native_manifest_test_support__pub.validate_manifest',
                    'source._parse',
                    'C15', 'C16', 'C45', 'C62',
                    'ADAPTERS_C30__pub.CEILINGS',
                    'ADAPTERS_C30__pub.ReadContext',
                    'ADAPTERS_C30__pub.open_regular',
                    'native_carrier_header__pub.canonical_native_header',
                    'work_journal__pub.PROJECT_DATABASE',
                    'work_journal__pub.append_sealed_events',
                    'work_journal__pub.journal_inbox',
                    'smalltest_support__pub.extension_directory',
                    'smalltest_support__pub.polling_source_watcher',
                    'scope_declaration_test_support__pub.write_scope_unit_declarations',
                    'legacy_selection_test_support__pub.select_legacy_project',
                    'model_host_pkg2__pub.reviewed_native_model',
                    'structure_host_pkg3__pub.read_structure',
                ]},
            },
            'io': {
                'server': {
                    'candidate_test_image_build': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'module': 'LAYER_3_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP.docker.candidate_image_cli',
                        'arguments': ['build', '--project-root', '<project-root>', '--attempt', '<attempt-id>', '--scratch', '<attempt-directory>', '[--packaged-assets]'],
                    },
                    'candidate_test_image_cleanup': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'module': 'LAYER_3_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP.docker.candidate_image_cli',
                        'arguments': ['cleanup', '--project-root', '<project-root>', '--attempt', '<attempt-id>', '--image', '<image-id>'],
                    },
                    'shared_mcp_launcher': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/shared_mcp_launcher.py',
                    },
                    'shared_runtime_mcp': {
                        'transport': 'http',
                        'path': '/anechoic/mcp',
                        'protocol': 'mcp',
                    },
                },
                'client': [
                    {'component': 'C45', 'interface': 'previous_image_model_claim_selection'},
                    {'component': 'C50', 'interface': 'image_model_compile'},
                ],
            },
        },
    ),
)
```
