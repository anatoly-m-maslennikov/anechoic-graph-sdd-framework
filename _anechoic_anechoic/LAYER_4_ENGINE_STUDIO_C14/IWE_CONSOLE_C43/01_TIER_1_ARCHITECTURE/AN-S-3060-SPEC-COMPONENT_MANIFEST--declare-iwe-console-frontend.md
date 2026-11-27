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
  version: 15
  updated_at: "2026-11-27T20:33:21.610274+00:00"
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
        'client': [{'component': 'C21', 'interface': 'tool_rest'}]},
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
Submit the current View's SQL to the Project HTTP API. Run and Run & Save
display only the page belonging to the acknowledged View revision and the
nonempty query ID in the Run receipt. Preserve editor SQL and any result
the Project already saved. Reject a missing or mismatched receipt revision
or a missing query ID before fetching. Reject a page with a missing or
different query ID before display.

Check displays the verdict for the current SQL and preserves the previous
Run result. Changing SQL clears that Check verdict. Display an error
when the Project API refuses or fails a request.

#### References

AN-S-2328, AN-S-2549, AN-S-3060, and AN-T-2947.

```python trace
declare_trace_contract(
    action='workbench_frontend_run_view',
    invariant={'forbid_effect': ('C46.discard_saved_result',)},
    cases={'succeeded': {'must_effect': (('C46.acknowledged_view', 'acknowledged'),
                               ('C21.view_run', 'returned'),
                               ('C21.view_fetch', 'returned'),
                               ('C46.result_display', 'shown')),
               'same_values': ((('acknowledged_view', 'revision'),
                                ('run_reply', 'revision')),
                               (('run_reply', 'query_id'),
                                ('first_page_received', 'query_id'))),
               'value_types': {('acknowledged_view', 'revision'): 'integer',
                               ('run_reply', 'revision'): 'integer',
                               ('run_reply', 'query_id'): 'nonempty_string',
                               ('first_page_received', 'query_id'): 'nonempty_string'},
               'must_precede': ((('C21.view_fetch', 'returned'),
                                 ('C46.result_display', 'shown')),)},
 'revision_refused': {'must_effect': (('C46.run_error', 'shown'),),
                      'forbid_effect': ('C46.result_display',
                                        'C21.view_fetch')},
 'missing_query_id': {'must_effect': (('C46.run_error', 'shown'),),
                      'forbid_effect': ('C46.result_display',
                                        'C21.view_fetch')},
 'page_refused': {'must_effect': (('C46.run_error', 'shown'),),
                  'forbid_effect': ('C46.result_display',)},
 'failed': {'forbid_effect': ('C46.result_display',)}},
)
```

### Call the Backend Tool API from the Console page

#### Guarantee

Read the admitted Project instance from the `anechoic-project-instance`
meta element. Require 64 lowercase hexadecimal characters before sending
a request. Send Tool calls to same-origin `POST /` with
`X-Anechoic-Project-Instance`.

Send the canonical Tool envelope with `name`, `arguments`, `session_id`,
and `public_base_url`. Supply `arguments.project_root` when the page
URL selects a Project root.

Return `result.value` only for a valid Tool result with a matching Project
receipt. Preserve a typed refusal's code and message, including on HTTP
200. Reject a malformed envelope. Keep the existing Console Run, Check,
page delivery, and embedded MCP behavior.

#### References

AN-S-3044@73 and AN-T-4085@1-draft.

```python trace
declare_trace_contract(
    action='workbench_frontend_call_tool',
    cases={'succeeded': {'must_effect': (('C21.tool_rest',
                                'requested',
                                {'endpoint': 'POST /',
                                 'instance_header': 'X-Anechoic-Project-Instance'}),
                               ('C46.project_receipt', 'matched')),
               'same_values': ((('rest_requested', 'instance_id'),
                                ('project_receipt', 'instance_id')),),
               'value_types': {('rest_requested', 'instance_id'): 'nonempty_string',
                               ('project_receipt', 'instance_id'): 'nonempty_string'},
               'must_precede': ((('C21.tool_rest', 'requested'),
                                 ('C46.project_receipt',
                                  'matched')),)},
 'refused': {'must_effect': (('C21.tool_rest',
                              'requested',
                              {'endpoint': 'POST /',
                               'instance_header': 'X-Anechoic-Project-Instance'}),
                             ('C46.typed_refusal', 'preserved')),
             'same_values': ((('typed_refusal', 'code'),
                              ('return_refusal', 'code')),
                             (('typed_refusal', 'message'),
                              ('return_refusal', 'message'))),
             'forbid_effect': ('C46.project_receipt',)},
 'receipt_refused': {'must_effect': (('C21.tool_rest',
                                      'requested',
                                      {'endpoint': 'POST /',
                                       'instance_header': 'X-Anechoic-Project-Instance'}),),
                     'forbid_effect': ('C46.project_receipt',)},
 'invalid_page_instance': {'forbid_effect': ('C21.tool_rest',)},
 'invalid_response': {'must_effect': (('C21.tool_rest',
                                       'requested',
                                       {'endpoint': 'POST /',
                                        'instance_header': 'X-Anechoic-Project-Instance'}),),
                      'forbid_effect': ('C46.project_receipt',)}},
)
```
