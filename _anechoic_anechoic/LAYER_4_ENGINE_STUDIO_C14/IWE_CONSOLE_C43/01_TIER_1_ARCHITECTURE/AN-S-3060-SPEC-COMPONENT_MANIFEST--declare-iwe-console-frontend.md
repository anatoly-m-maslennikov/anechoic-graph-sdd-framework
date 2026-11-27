---
atom_family: SPEC
atom_id: AN-S-3060
container:
  component: C43
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 11
  updated_at: "2026-11-26T15:52:28.487067+00:00"
---

## Summary

Declare IWE_CONSOLE_FRONTEND

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C46',
    name='IWE_CONSOLE_FRONTEND',
    lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': ['src.lib.lib__shared']},
          'exports': {'FEATURE_IWE_CONSOLE_FRONTEND__shared': None,
                      'src.lib.lib__shared': {'shared': ['C46',
                                                         'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/src',
                                                         'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/FEATURE_IWE_CONSOLE_FRONTEND__tests']},
                      'FEATURE_IWE_CONSOLE_FRONTEND__shared.WorkbenchApi': None,
                      'FEATURE_IWE_CONSOLE_FRONTEND__shared.WorkspaceApi': None,
                      'FEATURE_IWE_CONSOLE_FRONTEND__shared.HttpOperationCaller': None,
                      'FEATURE_IWE_CONSOLE_FRONTEND__shared.McpAppTransport': None,
                      'FEATURE_IWE_CONSOLE_FRONTEND__shared.OperationCaller': None}},
 'io': {'server': {'source_imports': {'transport': 'cli',
                                      'runner': 'node',
                                      'path': 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/scripts/import-graph-scanner.ts'},
                   'source_function_sizes': {'transport': 'cli',
                                             'runner': 'node',
                                             'path': 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/scripts/source-function-sizes.ts'}},
        'client': [{'component': 'C21', 'interface': 'workbench_http'}]},
 'state': {'reads': ['selected Project Workspace and View',
                     'query pages and check verdicts'],
           'writes': ['browser preferences',
                      'editor and View display state',
                      'standalone browser drafts']}}
```

## Component Contract

### Show IWE Console query results in the browser

#### Guarantee

Open the Workspace of the selected Project before enabling SQL input.
Submit the current View's SQL to the Project HTTP API. Run displays the
returned columns and rows and preserves the SQL in the editor.

Check displays the verdict for the current SQL and preserves the previous
Run result. Changing SQL clears that Check verdict. Display an error
when the Project API refuses or fails a request.

#### References

AN-S-2328, AN-S-2549, AN-S-3060, and AN-T-2947.
