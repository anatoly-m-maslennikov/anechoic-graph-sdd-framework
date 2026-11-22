---
atom_family: SPEC
atom_id: AN-S-3037
container:
  component: C00
tier: -1
context:
  template: project_manifest
  lens: SPEC
state:
  status: "archived"
  version: 16
  updated_at: "2026-11-22T10:58:11.244100+00:00"
---

## Summary

Declare Anechoic

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ProjectManifest

declare_entity(
    entity_name='Project Manifest',
    instance=ProjectManifest(
        name='Anechoic',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
        prefix='AN',
        parameters={
            'project': {'root': {'prefix': 'underscore'}},
            'project_mcp': {
                'release_workflows_enabled': True,
                'http_port': 56317,
                'tool_blacklist': ['release_version', 'public.release'],
            },
            'runtime': {
                'journal': {'storage': 'duckdb'},
                'workbench': {
                    'storage': 'disk',
                    'inline_result_limit_kib': 4,
                    'import_graph': {
                        'python_roots': [
                            'LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS',
                            'LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP',
                            'LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC',
                            'LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43',
                            'LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH',
                            'LAYER_5_FRAMEWORK_DELIVERY/RELEASE_VERSION',
                            'LAYER_3_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/ACTION_PROMPTS/RMED_ATOM_REVIEW',
                            '.',
                            'LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH',
                            'LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker',
                            'LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND',
                            'LAYER_3_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/ACTION_PROMPTS/RMED_ATOM_REVIEW/repair',
                            'LAYER_3_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/ACTION_PROMPTS/RMED_ATOM_REVIEW/RMED_ATOM_REVIEW__tests',
                            'LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS',
                            'RUNTIME_SETUP',
                            'LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/VALIDATE_ATOMS',
                            'LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/RELEASE_VERSION',
                            'LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_CODEX',
                            'LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests/assets/content_declaration_schema',
                            'LAYER_5_FRAMEWORK_DELIVERY/PUBLIC_RELEASE',
                        ],
                        'python_image_imports': {
                            'LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/native_model_selector.py': [
                                'APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.content_schema',
                                'APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.header_columns',
                                'APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store',
                            ]
                        },
                    },
                },
            },
        },
    ),
)
```

### Prose Claim

At Workbench startup, `parameters.runtime.workbench.inline_result_limit_kib` is a whole positive KiB value. Workbench automatically sends complete query results up to this limit inline and larger results to files.
