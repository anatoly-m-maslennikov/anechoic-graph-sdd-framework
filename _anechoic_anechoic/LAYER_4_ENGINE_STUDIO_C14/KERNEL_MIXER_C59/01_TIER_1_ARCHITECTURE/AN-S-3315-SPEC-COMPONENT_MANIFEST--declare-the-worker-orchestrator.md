---
atom_family: SPEC
atom_id: AN-S-3315
container:
  component: C59
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 6
  updated_at: "2026-11-26T15:52:28.214607+00:00"
---
## Summary

Declare the Worker Orchestrator

## Purpose

Start short-lived Manifest Compiler workers and own their run records.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C66',
    name='Orchestrator',
    lens_whitelist=['DES', 'SPEC'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': []},
          'exports': {'ORCHESTRATOR_C66__shared.Orchestrator': None}},
 'io': {'server': {'compiler_worker': {'transport': 'in_process',
                                       'entry': 'ORCHESTRATOR_C66__shared.Orchestrator.run_worker'},
                   'worker_runs': {'transport': 'http',
                                   'socket': 'private Kernel Unix socket',
                                   'path': 'GET /jobs/worker-runs',
                                   'query': {'instance_id': '<instance-id>'}}},
        'client': [{'component': 'C50', 'interface': 'manifest_compile'}]},
 'state': {'reads': ['compiler exit status and process identity'],
           'writes': ['active Worker runs',
                      'latest terminal Worker run per kind']}}
```

## Component Contract

### Track Manifest Compiler Worker runs

#### Guarantee

For the admitted Project, start Model builds and Structure refreshes in
short-lived processes. Reap a process when it finishes or exceeds its
deadline. Report the active runs and the latest terminal run of each kind
through the declared Worker Run interface. Each record identifies the
run, its kind, the process if it started, and its status.

#### References

AN-T-2944 and AN-S-3088.
