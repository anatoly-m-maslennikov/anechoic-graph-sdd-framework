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
  status: archived
  version: 17
  updated_at: "2026-11-28T13:46:19+00:00"
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
 'io': {'server': {'console_view': {'transport': 'in_process',
                                    'entry': 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/src/App.svelte'},
                   'source_imports': {'transport': 'cli',
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

### Render and refine the selected Console View

#### Guarantee

Keep editable SQL with each View. Render Table, Document, Graph, Imports,
or Structure results. Reuse the Document presentation in the modal,
a Console tab, and the right pane. Show version history, related Atoms,
and contained Atoms. Use the selected Project capability to create or
reopen Drafts, autosave every five seconds, and change status.

#### Semantics

The render observation describes display of the current query result.
The trace cases bind example inputs to observable results.

```python trace
declare_trace_contract(action='render_console_view', interface='console_view',
                       transport='in_process', cases={'failed': {'forbid_effect': ('C46.console',)},
 'succeeded': {'must_effect': (('C46.console', 'view_displayed'),)}})
```

### Graph and Imports observations

The graph keeps query matches at depth zero. Selected relation types govern
expansion and displayed edges. Bindings, layout, and import violations remain
visible. Invalid depth and missing occurrence keys report errors.
Both Graph and Imports default to vertical. A trailing `VERTICAL` or
`HORIZONTAL` on either View directive chooses the layout.
Spec Bindings follow the exact revision of each matched Atom. An exact
query reference remains exact when the user opens its document.

```python trace
declare_trace_contract(action='observe_console_graph', cases={'depth_zero': {'must_effect': (('C46.graph_observation', 'visible', {'nodes': 'AN-S-1', 'edges': ''}),)},
 'depth_one': {'must_effect': (('C46.graph_observation',
                                'visible',
                                {'nodes': 'AN-S-1|AN-S-2', 'edges': 'AN-S-1 → AN-S-2: uses'}),)},
 'depth_two': {'must_effect': (('C46.graph_observation',
                                'visible',
                                {'nodes': 'AN-S-1|AN-S-2|AN-S-3',
                                 'edges': 'AN-S-1 → AN-S-2: uses|AN-S-2 → AN-S-3: uses'}),)},
 'horizontal': {'must_effect': (('C46.graph_observation',
                                 'visible',
                                 {'nodes': 'AN-S-1|AN-S-2', 'edges': 'AN-S-1 → AN-S-2: uses'}),)},
 'bindings': {'must_effect': (('C46.graph_observation',
                               'visible',
                               {'nodes': 'AN-S-1|package:p|C01',
                                'edges': 'package:p → AN-S-1: Spec Binding|component:C01 → AN-S-1: Spec '
                                         'Binding'}),)},
 'exact_bindings': {'must_effect': (('C46.graph_observation', 'visible',
                                     {'nodes': 'AN-S-1@2|AN-S-2|package:p|C01',
                                      'edges': 'AN-S-1@2 → AN-S-2: uses|package:p → AN-S-1@2: Spec Binding|component:C01 → AN-S-1@2: Spec Binding'}),)},
 'invalid_depth': {'must_effect': (('C46.graph_observation',
                                    'visible',
                                    {'error': 'Depth must be a non-negative whole number.'}),)},
 'imports_scope': {'must_effect': (('C46.graph_observation',
                                    'visible',
                                    {'nodes': 'a.py|b.py',
                                     'edges': 'module:a → module:b: Imports · violation',
                                     'layout': 'horizontal',
                                     'red': True}),)},
 'imports_missing_key': {'must_effect': (('C46.graph_observation', 'visible', {'error': 'occurrence_key'}),)}})
```


### Atom document observations

#### Guarantee

Resolve a Current or exact reference through the same Document view.
Open it in the requested destination and preserve the query order.
Link displayed Atom references in result cells, grouped results,
full cell values, Document headers and bodies, Draft relation lists,
and Structure purposes. In a canonical filename, the link opens the
reference before the filename's description.

```python trace
declare_trace_contract(action='observe_atom_document', cases={'table_modal_bare': {'must_effect': (('C46.document_observation',
                                       'observed',
                                       {'source': 'table',
                                        'reference': 'AN-S-1',
                                        'destination': 'modal',
                                        'exact_ref': 'AN-S-1@2'}),)},
 'table_modal_exact': {'must_effect': (('C46.document_observation',
                                        'observed',
                                        {'source': 'table',
                                         'reference': 'AN-S-1@1',
                                         'destination': 'modal',
                                         'exact_ref': 'AN-S-1@1'}),)},
 'table_pane': {'must_effect': (('C46.document_observation',
                                 'observed',
                                 {'source': 'table',
                                  'reference': 'AN-S-1',
                                  'destination': 'pane',
                                  'exact_ref': 'AN-S-1@2'}),)},
 'table_tab': {'must_effect': (('C46.document_observation',
                                'observed',
                                {'source': 'table',
                                 'reference': 'AN-S-1',
                                 'destination': 'tab',
                                 'exact_ref': 'AN-S-1@2'}),)},
 'graph_modal': {'must_effect': (('C46.document_observation',
                                  'observed',
                                  {'source': 'graph',
                                   'reference': 'AN-S-1',
                                   'destination': 'modal'}),)},
 'graph_pane': {'must_effect': (('C46.document_observation',
                                 'observed',
                                 {'source': 'graph',
                                  'reference': 'AN-S-1',
                                  'destination': 'pane'}),)},
 'graph_tab': {'must_effect': (('C46.document_observation',
                                'observed',
                                {'source': 'graph',
                                 'reference': 'AN-S-1',
                                 'destination': 'tab'}),)},
 'stack_collapsed': {'must_effect': (('C46.document_observation',
                                      'observed',
                                      {'source': 'document',
                                       'operation': 'hide_all',
                                       'visible': 'canonical_filename'}),)},
 'stack_expanded': {'must_effect': (('C46.document_observation',
                                     'observed',
                                     {'source': 'document',
                                      'operation': 'expand_all',
                                      'visible': 'full_document'}),)},
 'related_navigation': {'must_effect': (('C46.document_observation',
                                         'observed',
                                         {'source': 'document',
                                          'operation': 'open_related',
                                          'reference': 'AN-S-2'}),)},
 'contained_navigation': {'must_effect': (('C46.document_observation',
                                           'observed',
                                           {'source': 'document',
                                            'operation': 'open_contained',
                                            'reference': 'AN-T-5'}),)},
 'document_sections': {'must_effect': (('C46.document_observation',
                                        'observed',
                                        {'source': 'document',
                                         'history': True,
                                         'related': True,
                                         'contained': True}),)}})
```

### SQL, View, and Diagnostics observations

#### Guarantee

Edit the SQL in the editor and render the selected result. Map health
and rebuild responses to the Diagnostics state and message.

```python trace
declare_trace_contract(action='edit_console_builder', output='component', must_effect=(('C46.builder', 'shown', {'sql': 'SELECT * FROM atoms WHERE "header.container.component" = \'C01\' LIMIT 5'}),))
```

```python trace
declare_trace_contract(action='edit_console_builder', output='tier', must_effect=(('C46.builder', 'shown', {'sql': 'SELECT * FROM atoms WHERE "header.tier" = 2 LIMIT 5'}),))
```

```python trace
declare_trace_contract(action='edit_console_builder', output='template', must_effect=(('C46.builder', 'shown', {'sql': 'SELECT * FROM atoms WHERE "header.context.template" = \'solution\' LIMIT 5'}),))
```

```python trace
declare_trace_contract(action='edit_console_builder', output='limit', must_effect=(('C46.builder', 'shown', {'sql': 'SELECT * FROM atoms LIMIT 3'}),))
```

```python trace
declare_trace_contract(action='edit_console_builder', output='invalid_limit', must_effect=(('C46.builder', 'rejected', {'sql': 'SELECT * FROM atoms LIMIT 5', 'error': 'Limit must be a non-negative integer.'}),))
```

When a Builder edit changes the SQL, update the selected View and run it.
Display the first page only when its query ID matches the Run receipt and
that receipt identifies the updated revision.

```python trace
declare_trace_contract(action='run_console_builder', effects={
    'update': ('C21.view_update', 'requested'),
    'updated': ('C21.view_update', 'succeeded'),
    'run': ('C21.view_run', 'requested'),
    'receipt': ('C21.view_run.query_id', 'returned'),
    'fetch': ('C21.view_fetch', 'requested'),
    'page': ('C21.view_fetch', 'succeeded'),
    'display': ('workbench_display', 'shown'),
}, cases={'edited_run': {
    'must_effect': ('update', 'updated', 'run', 'receipt', 'fetch', 'page', 'display'),
    'must_precede': (('update', 'updated'), ('updated', 'run'), ('run', 'receipt'),
                     ('receipt', 'fetch'), ('fetch', 'page'), ('page', 'display')),
    'same_values': (
        (('edited_run', 'view_id'), ('update_requested', 'view_id')),
        (('edited_run', 'sql'), ('update_requested', 'sql')),
        (('edited_run', 'revision'), ('update_requested', 'expected_revision')),
        (('edited_run', 'view_id'), ('update_returned', 'id')),
        (('edited_run', 'sql'), ('update_returned', 'sql')),
        (('edited_run', 'view_id'), ('run_requested', 'view_id')),
        (('update_returned', 'revision'), ('run_returned', 'revision')),
        (('edited_run', 'view_id'), ('fetch_requested', 'view_id')),
        (('run_returned', 'query_id'), ('first_page_received', 'query_id')),
        (('edited_run', 'view_id'), ('result_displayed', 'view_id')),
        (('edited_run', 'sql'), ('result_displayed', 'sql')),
        (('update_returned', 'revision'), ('result_displayed', 'revision')),
        (('run_returned', 'query_id'), ('result_displayed', 'query_id')),
    ),
}})
```

Recognize a trailing View directive at the top level of SQL. Allow SQL
comments between its words and after it. Ignore View words in SQL strings,
quoted identifiers, comments, and nested expressions.

```python trace
declare_trace_contract(action='select_console_view', output='table_default', must_effect=(('C46.view', 'shown', {'kind': 'table', 'layout': 'vertical'}),))
```

```python trace
declare_trace_contract(action='select_console_view', output='table', must_effect=(('C46.view', 'shown', {'kind': 'table', 'layout': 'vertical'}),))
```

```python trace
declare_trace_contract(action='select_console_view', output='doc', must_effect=(('C46.view', 'shown', {'kind': 'document', 'layout': 'vertical'}),))
```

```python trace
declare_trace_contract(action='select_console_view', output='document', must_effect=(('C46.view', 'shown', {'kind': 'document', 'layout': 'vertical'}),))
```

```python trace
declare_trace_contract(action='select_console_view', output='graph', must_effect=(('C46.view', 'shown', {'kind': 'graph', 'layout': 'vertical'}),))
```

```python trace
declare_trace_contract(action='select_console_view', output='graph_vertical', must_effect=(('C46.view', 'shown', {'kind': 'graph', 'layout': 'vertical'}),))
```

```python trace
declare_trace_contract(action='select_console_view', output='graph_horizontal', must_effect=(('C46.view', 'shown', {'kind': 'graph', 'layout': 'horizontal'}),))
```

```python trace
declare_trace_contract(action='select_console_view', output='imports', must_effect=(('C46.view', 'shown', {'kind': 'imports', 'layout': 'vertical'}),))
```

```python trace
declare_trace_contract(action='select_console_view', output='structure', must_effect=(('C46.view', 'shown', {'kind': 'structure', 'layout': 'vertical'}),))
```

```python trace
declare_trace_contract(action='select_console_view', output='document_multiple_refs', must_effect=(('C46.view', 'rejected', {'kind': 'document', 'error': 'Select a single Atom reference column for this view.'}),))
```

```python trace
declare_trace_contract(action='select_console_view', output='graph_multiple_refs', must_effect=(('C46.view', 'rejected', {'kind': 'graph', 'error': 'Select a single Atom reference column for this view.'}),))
```

```python trace
declare_trace_contract(action='inspect_console_diagnostics', output='healthy', must_effect=(('C46.diagnostics', 'shown', {'runtime': 'Healthy'}),))
```

```python trace
declare_trace_contract(action='inspect_console_diagnostics', output='starting', must_effect=(('C46.diagnostics', 'shown', {'runtime': 'Starting'}),))
```

```python trace
declare_trace_contract(action='inspect_console_diagnostics', output='unhealthy', must_effect=(('C46.diagnostics', 'shown', {'runtime': 'Unhealthy', 'issue': 'Bad source', 'ref': 'AN-S-1'}),))
```

```python trace
declare_trace_contract(action='inspect_console_diagnostics', output='unavailable', must_effect=(('C46.diagnostics', 'shown', {'runtime': 'Unhealthy'}),))
```

```python trace
declare_trace_contract(action='inspect_console_diagnostics', output='graph_success', must_effect=(('C46.diagnostics', 'shown', {'message': 'Realization Graph rebuild complete.'}),))
```

```python trace
declare_trace_contract(action='inspect_console_diagnostics', output='graph_refused', must_effect=(
    ('C46.diagnostics', 'rejected', {'error': 'Rebuild refused by fixture', 'worker': 'failed',
                                    'issue': 'Build input unavailable', 'ref': 'AN-S-1'}),))
```

```python trace
declare_trace_contract(action='inspect_console_diagnostics', output='all_success', must_effect=(('C46.diagnostics', 'shown', {'message': 'Project database rebuild complete.'}),))
```

```python trace
declare_trace_contract(action='inspect_console_diagnostics', output='all_refused', must_effect=(
    ('C46.diagnostics', 'rejected', {'error': 'Rebuild refused by fixture', 'worker': 'failed',
                                    'issue': 'Build input unavailable', 'ref': 'AN-S-1'}),))
```

### Atom lifecycle observations

#### Guarantee

Show lifecycle requests and their results in the Atom document. Save dirty Draft
edits before promotion and allow the user to reopen an existing Draft.
Offer removal only for relations authored in the Draft Header.
When a save is rejected, show its error and keep the unsaved input.
Do not send the promotion until the save succeeds.
When creating a Draft from Current, send its ID and version. Open the exact
Draft reference returned by the lifecycle operation.

```python trace
declare_trace_contract(action='observe_atom_lifecycle', cases={'task_edit': {'must_effect': (('C46.lifecycle_observation',
                                'observed',
                                {'autosave_seconds': 5,
                                 'removed_type': 'IS_SOLUTION_FOR',
                                 'removed_ref': 'AN-S-1',
                                 'authored_only': True,
                                 'publish_status': 'backlog',
                                 'current_status': 'in_queue',
                                 'summary_error': 'Changing a Summary is not supported.',
                                 'reopens_existing': True}),)},
 'configured_status': {'must_effect': (('C46.lifecycle_observation',
                                        'observed',
                                        {'current_status': 'waiting_review'}),)},
 'current_draft': {
     'must_effect': (('C21.atom_lifecycle_create_draft', 'requested'),
                     ('C21.atom_lifecycle_create_draft', 'succeeded'),
                     ('C21.iwe_console_atom_document', 'requested'),
                     ('C46.lifecycle_observation', 'observed')),
     'must_precede': (
         (('C21.atom_lifecycle_create_draft', 'requested'), ('C21.atom_lifecycle_create_draft', 'succeeded')),
         (('C21.atom_lifecycle_create_draft', 'succeeded'), ('C21.iwe_console_atom_document', 'requested')),
         (('C21.iwe_console_atom_document', 'requested'), ('C46.lifecycle_observation', 'observed')),
     ),
     'same_values': (
         (('current_draft', 'source_ref'), ('create_requested', 'ref_id')),
         (('current_draft', 'source_version'), ('create_requested', 'version')),
         (('draft_returned', 'ref_id'), ('document_requested', 'ref_id')),
         (('current_draft', 'source_ref'), ('observed', 'source_ref')),
         (('current_draft', 'source_version'), ('observed', 'source_version')),
         (('draft_returned', 'ref_id'), ('observed', 'draft_ref')),
     ),
 },
 'principle_create': {'must_effect': (('C46.lifecycle_observation',
                                       'observed',
                                       {'template': 'applicable_principle',
                                        'tier': 1,
                                        'lens': 'SPEC',
                                        'component': 'C00',
                                        'error': 'fixture stop'}),)},
 'spec_activate': {'must_effect': (('C46.lifecycle_observation',
                                    'observed',
                                    {'publish_status': 'ready',
                                     'current_status': 'active',
                                     'current_body': '## Summary\n\nCreated\n\nUpdated\n'}),)}})
```

Before leaving a dirty Draft, finish its save or obtain explicit confirmation
to discard its edits. A refused save keeps the editor and its pending changes.
Renaming an inactive View changes its name and keeps the active View selected.

If a save is in progress when newer edits are pending, wait for that save.
Send the newer edits with the timestamp it returns. Leave after the newer
save succeeds. If either save is refused, keep the editor and the newer edits.

```python trace
declare_trace_contract(action='guard_draft_editor', effects={
    'save': ('C21.atom_lifecycle_update', 'requested'),
    'saved': ('C21.atom_lifecycle_update', 'succeeded'),
    'failed': ('C21.atom_lifecycle_update', 'failed'),
    'pending_save': ('C21.atom_lifecycle_update', 'requested', {'phase': 'pending'}),
    'pending_saved': ('C21.atom_lifecycle_update', 'succeeded', {'phase': 'pending'}),
    'pending_failed': ('C21.atom_lifecycle_update', 'failed', {'phase': 'pending'}),
    'latest_save': ('C21.atom_lifecycle_update', 'requested', {'phase': 'latest'}),
    'latest_saved': ('C21.atom_lifecycle_update', 'succeeded', {'phase': 'latest'}),
    'latest_failed': ('C21.atom_lifecycle_update', 'failed', {'phase': 'latest'}),
    'unmounted': ('C46.draft_editor', 'unmounted'),
    'clean_unmount': ('C46.draft_editor', 'unmounted', {'dirty': False}),
    'retained': ('C46.draft_editor', 'retained', {'dirty': True}),
    'rename': ('C21.view_rename', 'requested'),
    'renamed': ('C21.view_rename', 'succeeded'),
    'shown': ('C46.view', 'shown'),
}, cases={
    'saved': {
        'must_effect': ('save', 'saved', 'clean_unmount'),
        'must_precede': (('save', 'saved'), ('saved', 'clean_unmount')),
        'same_values': (
            (('leave_dirty', 'draft_ref'), ('save_requested', 'ref_id')),
            (('leave_dirty', 'changes'), ('save_requested', 'changes')),
            (('save_requested', 'ref_id'), ('save_succeeded', 'ref_id')),
            (('save_succeeded', 'ref_id'), ('editor_unmounted', 'draft_ref')),
        ),
    },
    'discarded': {
        'must_effect': ('unmounted',),
        'same_values': (
            (('leave_dirty', 'draft_ref'), ('discard_confirmed', 'draft_ref')),
            (('leave_dirty', 'changes'), ('discard_confirmed', 'changes')),
            (('discard_confirmed', 'draft_ref'), ('editor_unmounted', 'draft_ref')),
        ),
    },
    'save_refused': {
        'must_effect': ('save', 'failed', 'retained'),
        'must_precede': (('save', 'failed'), ('failed', 'retained')),
        'same_values': (
            (('leave_dirty', 'draft_ref'), ('save_requested', 'ref_id')),
            (('leave_dirty', 'changes'), ('save_requested', 'changes')),
            (('leave_dirty', 'draft_ref'), ('editor_retained', 'draft_ref')),
            (('leave_dirty', 'changes'), ('editor_retained', 'changes')),
        ),
    },
    'rename_inactive': {
        'must_effect': ('rename', 'renamed', 'shown'),
        'must_precede': (('rename', 'renamed'), ('renamed', 'shown')),
        'same_values': (
            (('rename_inactive', 'view_id'), ('rename_requested', 'view_id')),
            (('rename_inactive', 'name'), ('rename_requested', 'name')),
            (('rename_requested', 'view_id'), ('rename_returned', 'id')),
            (('rename_requested', 'name'), ('rename_returned', 'name')),
            (('rename_inactive', 'active_view_id'), ('view_observed', 'active_view_id')),
        ),
    },
    'saved_after_pending': {
        'must_effect': ('pending_save', 'pending_saved', 'latest_save', 'latest_saved', 'clean_unmount'),
        'must_precede': (('pending_save', 'pending_saved'), ('pending_saved', 'latest_save'),
                         ('latest_save', 'latest_saved'), ('latest_saved', 'clean_unmount')),
        'same_values': (
            (('leave_dirty', 'draft_ref'), ('pending_save_requested', 'ref_id')),
            (('pending_save_requested', 'ref_id'), ('pending_save_succeeded', 'ref_id')),
            (('pending_save_succeeded', 'updated_at'), ('save_requested', 'expectedUpdatedAt')),
            (('leave_dirty', 'draft_ref'), ('save_requested', 'ref_id')),
            (('leave_dirty', 'changes'), ('save_requested', 'changes')),
            (('save_requested', 'ref_id'), ('save_succeeded', 'ref_id')),
            (('save_succeeded', 'ref_id'), ('editor_unmounted', 'draft_ref')),
        ),
    },
    'pending_save_refused': {
        'must_effect': ('pending_save', 'pending_failed', 'retained'),
        'forbid_effect': ('C21.view_focus',),
        'must_precede': (('pending_save', 'pending_failed'), ('pending_failed', 'retained')),
        'same_values': (
            (('leave_dirty', 'draft_ref'), ('pending_save_requested', 'ref_id')),
            (('leave_dirty', 'draft_ref'), ('editor_retained', 'draft_ref')),
            (('leave_dirty', 'changes'), ('editor_retained', 'changes')),
        ),
    },
    'latest_save_refused': {
        'must_effect': ('pending_save', 'pending_saved', 'latest_save', 'latest_failed', 'retained'),
        'forbid_effect': ('C21.view_focus',),
        'must_precede': (('pending_save', 'pending_saved'), ('pending_saved', 'latest_save'),
                         ('latest_save', 'latest_failed'), ('latest_failed', 'retained')),
        'same_values': (
            (('leave_dirty', 'draft_ref'), ('pending_save_requested', 'ref_id')),
            (('pending_save_requested', 'ref_id'), ('pending_save_succeeded', 'ref_id')),
            (('pending_save_succeeded', 'updated_at'), ('save_requested', 'expectedUpdatedAt')),
            (('leave_dirty', 'draft_ref'), ('save_requested', 'ref_id')),
            (('leave_dirty', 'changes'), ('save_requested', 'changes')),
            (('leave_dirty', 'draft_ref'), ('editor_retained', 'draft_ref')),
            (('leave_dirty', 'changes'), ('editor_retained', 'changes')),
        ),
    },
})
```

### Structure observations

#### Guarantee

Show the authored Component and Component Seed purposes. Open each
admitted Manifest by its exact reference. Link to the exact Active
Tier 0 Solutions that answer that Component Manifest revision.
The Seed's Solution link opens its Manifest with the embedded Solution.

```python trace
declare_trace_contract(action='observe_console_structure', cases={'component_purpose': {'must_effect': (('C46.structure_observation',
                                        'observed',
                                        {'purpose': 'Purpose AN-S-1@2'}),)},
 'component_manifest': {'must_effect': (('C46.structure_observation',
                                         'observed',
                                         {'reference': 'AN-S-1@2'}),)},
 'component_solution': {'must_effect': (('C46.structure_observation',
                                         'observed',
                                         {'reference': 'AN-S-2@9'}),)},
 'seed_purpose': {'must_effect': (('C46.structure_observation',
                                   'observed',
                                   {'purpose': 'Seed purpose'}),)},
 'seed_manifest': {'must_effect': (('C46.structure_observation',
                                    'observed',
                                    {'reference': 'AN-S-3@1'}),)},
 'seed_solution': {'must_effect': (('C46.structure_observation',
                                    'observed',
                                    {'reference': 'AN-S-3@1'}),)}})
```
