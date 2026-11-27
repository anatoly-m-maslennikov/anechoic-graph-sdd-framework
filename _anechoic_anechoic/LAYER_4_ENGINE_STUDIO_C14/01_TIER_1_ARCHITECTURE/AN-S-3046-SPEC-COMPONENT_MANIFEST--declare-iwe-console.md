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
  status: "active"
  version: 6
  updated_at: "2026-11-26T15:52:26.910434+00:00"
relations:
  CONTRIBUTES_TO:
  - AN-S-3330
---

## Summary

Declare IWE_CONSOLE

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
                                 'interface': 'workbench_http'}}},
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
