---
atom_family: SPEC
atom_id: AN-S-3060
container:
  component: C43
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 10
  updated_at: '2026-11-25T13:51:02.069251+00:00'
---

## Summary

Declare WORKBENCH_FRONTEND

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C46',
        name='WORKBENCH_FRONTEND',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'code': {
                'imports': {'only': ['src.lib.lib__shared']},
                'exports': {
                    'FEATURE_WORKBENCH_FRONTEND__shared': None,
                    'src.lib.lib__shared': {'shared': ['C46', 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/src',
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/FEATURE_WORKBENCH_FRONTEND__tests']},
                    'FEATURE_WORKBENCH_FRONTEND__shared.WorkbenchApi': None,
                    'FEATURE_WORKBENCH_FRONTEND__shared.WorkspaceApi': None,
                    'FEATURE_WORKBENCH_FRONTEND__shared.HttpOperationCaller': None,
                    'FEATURE_WORKBENCH_FRONTEND__shared.McpAppTransport': None,
                    'FEATURE_WORKBENCH_FRONTEND__shared.OperationCaller': None,
                },
            },
            'io': {
                'server': {
                    'workbench_frontend_run_view': {
                        'outcomes': {'succeeded': {
                            'must_effect': [('C21.view_run.query_id', 'returned'), ('workbench_display', 'shown')],
                            'forbid_effect': ['C21.view_run.malformed_reply', 'workbench_save_error'],
                        }, 'partial': {
                            'must_effect': [('C21.view_run.query_id', 'returned'), ('C21.view_run.save_error', 'returned'),
                                            ('workbench_save_error', 'shown'), ('workbench_display', 'shown')],
                            'forbid_effect': ['C21.view_run.malformed_reply'],
                        }, 'run_failed': {
                            'must_effect': [('C21.view_run.error', 'returned'), ('workbench_run_error', 'shown')],
                            'forbid_effect': ['C21.view_fetch', 'workbench_display', 'workbench_save_error'],
                        }, 'failed': {
                            'must_effect': [('workbench_run_error', 'shown')],
                        }},
                    },
                    'workbench_frontend_check_view': {'outcomes': {
                        'checked': {
                            'must_effect': (
                                ('project_api.view_check', 'returned', {'sql': 'current'}),
                                ('workbench_check_verdict', 'shown_for_current_sql'),
                                ('workbench_previous_run', 'preserved'),
                            ),
                            'forbid_effect': ('workbench_replace_previous_run', 'workbench_show_stale_check_verdict'),
                        },
                        'failed': {
                            'must_effect': (('workbench_prior_check_verdict', 'cleared'), ('workbench_check_error', 'shown'), ('workbench_previous_run', 'preserved')),
                            'forbid_effect': ('workbench_replace_previous_run', 'workbench_check_verdict', 'workbench_show_stale_check_verdict'),
                        },
                    }},
                    'workbench_frontend_edit_sql': {'outcomes': {
                        'changed': {
                            'must_effect': (('workbench_prior_check_verdict', 'cleared'), ('workbench_previous_run', 'preserved')),
                            'forbid_effect': ('workbench_replace_previous_run', 'workbench_check_verdict', 'workbench_show_stale_check_verdict'),
                        },
                    }},
                    'source_imports': {'transport': 'cli', 'runner': 'node',
                                       'path': 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/scripts/import-graph-scanner.ts'},
                    'source_function_sizes': {
                        'transport': 'cli',
                        'runner': 'node',
                        'path': 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/scripts/source-function-sizes.ts',
                    },
                },
                'client': [{'component': 'C21', 'interface': 'workbench_http', 'transport': 'http',
                            'routes': ['POST /anechoic/{project_name}/api/view_run']}],
            },
            'state': {
                'reads': ['selected Project Workspace and View', 'query pages and check verdicts'],
                'writes': ['browser preferences', 'editor and View display state', 'standalone browser drafts'],
            },
        },
    ),
)
```
