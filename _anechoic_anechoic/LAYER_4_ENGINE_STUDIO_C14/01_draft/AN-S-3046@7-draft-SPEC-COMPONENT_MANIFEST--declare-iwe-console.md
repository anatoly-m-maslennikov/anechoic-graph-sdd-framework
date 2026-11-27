---
atom_family: SPEC
atom_id: AN-S-3046
container:
  component: C14
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 7
  updated_at: "2026-11-27T09:32:44Z"
relations:
  CONTRIBUTES_TO:
  - AN-S-3330
---

## Summary

Declare IWE_CONSOLE

## Purpose

Let users query a Project and browse its Atoms, Structure, and imports.
Let users run supported lifecycle and rebuild operations.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C43',
    name='IWE_CONSOLE',
    lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': ['project_database__pub.console_state_path'], 'exports': {}},
 'io': {'client': {'workbench': {'component': 'C21',
                                 'interface': 'workbench_http'},
                   'console_view': {'component': 'C46', 'interface': 'console_view'}}},
 'state': {'reads': [], 'writes': []}}
```

## Component Contract

### Provide a Project IWE Console

#### Guarantee

Provide a browser Workspace for an admitted Project and expose its IWE Console
operations through the Project interface. A View holds SQL and its result;
Run and Check use the selected Project. Report failed operations to the caller.

The browser maintains local drafts and display preferences. The Backend owns
Project operation dispatch; the Kernel owns query execution and projection.
Saved items and transient results follow their respective owners' lifetimes.
Provide the IWE Console MCP App resource and the static Realization Graph through
their respective Components.

### Operate the selected Project in IWE Console

#### Guarantee

Expose SQL Views and their Table, Document, Graph, Imports, and Structure
results for the selected Project. Open Atom documents in the requested
destination and route lifecycle and rebuild operations to the bound Project.
Use the admitted Project identity even when two Projects have the same name.
Show completion only after the selected Project returns a successful receipt.

```python trace
declare_trace_contract(action='operate_console', effects={
    'dispatch': ('C21.workbench_http', 'dispatched'),
    'receipt': ('C21.workbench_http', 'succeeded'),
    'display': ('C46.console', 'view_displayed'),
    'complete': ('C43.console', 'console_operation_completed'),
}, cases={
    'failed': {'forbid_effect': ('C43.console',)},
    'succeeded': {
        'must_effect': ('dispatch', 'receipt', 'display', 'complete'),
        'must_precede': (('dispatch', 'receipt'), ('receipt', 'display'), ('display', 'complete')),
        'same_values': (
            (('requested', 'project'), ('dispatched', 'project')),
            (('requested', 'project'), ('received', 'project')),
            (('requested', 'project'), ('render_view', 'project')),
            (('requested', 'project'), ('completed', 'project')),
        ),
    },
})
```
