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
  status: "active"
  version: 23
  updated_at: '2026-11-27T17:52:19.903351+00:00'
---

## Summary

Anechoic project

## Purpose

Help Operators create, deliver, run, and maintain feasible Projects with AI Agents while using their resources more efficiently.

## Formal Manifest

```python anechoic-edsl
from anechoic.model import ComponentManifest

ComponentManifest(
    name='Anechoic',
    lens_whitelist=[
        'DES', 'DOM/CONT', 'DOM/ONT', 'DOM/MTD',
        'DevOps', 'QA', 'SPEC', 'SWD',
    ],
    prefix='AN',
    parameters={
        'root': {'prefix': 'underscore'},
        'folder_layout': {
            'active_spec_by_tier': {
                '0': '.',
                '1': '01_TIER_1_ARCHITECTURE',
                '2+': '_{lens}/{sublenses}',
            },
        },
        'project_mcp': {
            'release_workflows_enabled': True,
            'tool_blacklist': ['release_version', 'public.release'],
            'inline_result_limit_kib': 4,
        },
        'runtime': {
            'duck_db.storage': 'disk',
            'journal.storage': 'duckdb',
        },
    },
)
```

## Domain Lenses

`DOM/ONT` (Ontology) is declarative. It defines the kinds of entities in a
Domain and the rules that apply to them.

`DOM/MTD` (Methodology) is imperative. It describes actions and workflows
for working in the Domain.

## Folder Layout

The Tier -1 Project Manifest is at the repository root.
The Project control directory for Anechoic is `_anechoic_anechoic/`.
The `root.prefix` setting selects a leading underscore or dot
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
