---
atom_family: SPEC
atom_id: AN-S-3379
container:
  component: C62
tier: 1
context:
  template: DECISION
  lens: SPEC
relations:
  IS_SOLUTION_FOR:
  - AN-S-3186@5-draft
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T10:58:34Z'
---

## Summary

Build and host the initial Model and Structure for a selected Project.

## Claim

### Prose Claim

Manifest Runtime requests a build, opens the admitted Model, publishes its
matching Structure, and yields both to its caller.

For Structure refresh, pin the admitted Model before requesting a Worker.
Verify the replacement fingerprint against that Model before publishing.
On Worker or validation failure, retain the current snapshot.

### Formal Claim

```python
component_workflow(
    component='C62',
    action='manifest_runtime_start',
    machine={
        'id': 'c62_manifest_runtime_start',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'runtime_opened': {'target': 'admitting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'admitting': {'on': {
                'project_admitted': {'target': 'step_1', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C62.project_binding', 'outcome': 'admitted'}}},
            }},
            'step_1': {'on': {
                'request_model_build': {'target': 'step_2', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C66', 'detail': {
                        'interface': 'compiler_worker',
                        'transport': 'in_process',
                        'entry': 'ORCHESTRATOR_C66__shared.Orchestrator.run_worker',
                        'action': 'manifest_compiler_worker_run',
                    }}}},
            }},
            'step_2': {'on': {
                'compiler_worker_completed': {'target': 'verifying_model_attestation', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C66.worker_run', 'outcome': 'completed',
                     'detail': {'component': 'C66', 'action': 'manifest_compiler_worker_run',
                                'output': 'completed'}}}},
                'compiler_worker_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'verifying_model_attestation': {'on': {
                'model_attestation_verified': {'target': 'verifying', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C62.model_attestation', 'outcome': 'verified'}}},
                'artifact_rejected': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'verifying': {'on': {
                'fingerprint_verified': {'target': 'accepting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C62.fingerprint', 'outcome': 'verified'}}},
                'artifact_rejected': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'accepting': {'on': {
                'artifacts_accepted': {'target': 'publishing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C62.artifacts', 'outcome': 'accepted'}}},
            }},
            'publishing': {'on': {
                'structure_published': {'target': 'step_3', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C62.structure', 'outcome': 'published'}}},
            }},
            'step_3': {'on': {
                'yield_admitted_artifacts': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

```python
component_workflow(
    component='C62',
    action='manifest_runtime_refresh_structure',
    machine={
        'id': 'c62_manifest_runtime_refresh_structure',
        'initial': 'ready',
        'states': {
            'ready': {'on': {
                'refresh_requested': {'target': 'pinning', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'pinning': {'on': {
                'admitted_model_pinned': {'target': 'dispatching', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C62.admitted_model', 'outcome': 'pinned'}}},
            }},
            'dispatching': {'on': {
                'request_structure_refresh': {'target': 'waiting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C66', 'detail': {
                        'interface': 'compiler_worker', 'transport': 'in_process',
                        'entry': 'ORCHESTRATOR_C66__shared.Orchestrator.run_worker',
                        'action': 'manifest_compiler_worker_run',
                    }}}},
            }},
            'waiting': {'on': {
                'refresh_worker_completed': {'target': 'verifying', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C66.worker_run', 'outcome': 'completed',
                     'detail': {'component': 'C66', 'action': 'manifest_compiler_worker_run',
                                'output': 'completed'}}}},
                'refresh_worker_failed': {'target': 'retaining', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C66.compiler_worker', 'outcome': 'failed'}}},
                'refresh_worker_timed_out': {'target': 'retaining', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C66.worker_run', 'outcome': 'timed_out',
                     'detail': {'component': 'C66', 'action': 'manifest_compiler_worker_run',
                                'output': 'timed_out'}}}},
            }},
            'verifying': {'on': {
                'replacement_fingerprint_verified': {'target': 'publishing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C62.refresh_fingerprint', 'outcome': 'verified'}}},
                'replacement_rejected': {'target': 'retaining', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C62.refresh_fingerprint', 'outcome': 'rejected'}}},
            }},
            'publishing': {'on': {
                'replacement_published': {'target': 'published', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C62.structure_replacement', 'outcome': 'published_atomically'}}},
            }},
            'published': {'on': {
                'refresh_succeeded': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'retaining': {'on': {
                'previous_snapshot_retained': {'target': 'retained', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C62.previous_structure', 'outcome': 'retained'}}},
            }},
            'retained': {'on': {
                'refresh_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
C66 reports Worker completion. C62 verifies the Model attestation and
fingerprint before accepting and publishing the Model and Structure.
