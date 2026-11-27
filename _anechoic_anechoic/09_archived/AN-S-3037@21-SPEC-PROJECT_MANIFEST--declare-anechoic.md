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
  version: 21
  updated_at: "2026-11-27T17:24:48.156937+00:00"
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
        lens_whitelist=['DES', 'DOM/CONT', 'DOM/ONT', 'DOM/MTD', 'DevOps', 'QA', 'SPEC', 'SWD'],
        prefix='AN',
        parameters={
            'project': {
                'root': {'prefix': 'underscore'},
                'folder_layout': {
                    'active_spec_by_tier': {
                        '0': '.',
                        '1': '01_TIER_1_ARCHITECTURE',
                        '2+': '_{lens}/{sublenses}',
                    },
                },
            },
            'project_mcp': {
                'release_workflows_enabled': True,
                'http_port': 7777,
                'tool_blacklist': ['release_version', 'public.release'],
            },
            'runtime': {
                'journal': {'storage': 'duckdb'},
                'iwe_console': {
                    'storage': 'disk',
                    'inline_result_limit_kib': 4,
                    'import_graph': {
                        'python_image_imports': {
                            'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/native_model_selector.py': [
                                'APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.content_schema',
                                'APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.header_columns',
                                'APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store',
                                'LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.content_schema',
                                'LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.header_columns',
                                'LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.query_store',
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

At IWE Console startup, `parameters.runtime.iwe_console.inline_result_limit_kib` is a whole positive KiB value. Workbench automatically sends complete query results up to this limit inline and larger results to files.

### Domain Lenses

`DOM/ONT` (Ontology) is declarative. It defines the kinds of entities in a
Domain and the rules that apply to them.

`DOM/MTD` (Methodology) is imperative. It describes actions and workflows
for working in the Domain.

### Folder Layout

The Tier -1 Project Manifest and Project Goal are at the repository root.
The Project control directory for Anechoic is `_anechoic_anechoic/`.
The `project.root.prefix` setting selects a leading underscore or dot
for the control directory.

The Tier rules for Active SPEC Atoms are relative to the owning Project
control or Component directory. Tier 0 uses the owning directory.
Tier 1 uses `01_TIER_1_ARCHITECTURE/`. Tier 2 and above use the
authored Lens. A single underscore marks the first Lens folder.
Sublenses use plain folder names, as in `_DES/DOM/` and `_DES/IO/`.

Two underscores mark the reserved branches `__TICKETS/` and
`__PROJECT_CONFIG/` under the Project control directory.
Each owner uses `01_draft/`, `02_ready/`, and `09_archived/`
for SPEC Drafts, Ready Atoms, and Archives.
