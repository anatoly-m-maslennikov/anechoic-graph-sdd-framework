---
atom_family: SPEC
atom_id: AN-S-3363
container:
  component: C68
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3339@25-draft
state:
  status: draft
  version: 4
  updated_at: '2026-11-25T10:37:16Z'
---

## Summary

Model the Orchestrator rebuild flow

## Claim

### Prose Claim

An accepted explicit rebuild clears the retained input proof and starts a
cold Worker. Starting the Worker and receiving its sealed snapshot are
distinct events. After receipt, request full Kernel admission through
`database_api` over HTTP, using route `admit` and operation `PUT /generation`.
Observe the generation commit before the admission outcome. On admitted
provider failure, observe retention of the previous generation and report
failure without publishing replacement IDs.

Record whether successful admission requires a reuse proof write. If it
does, store the proof before reporting the admitted generation. Otherwise
return replacement IDs. Return replacement IDs after storing any required
proof and before reporting success. Report a failure or accepted Worker abort at the
corresponding exit.

The Formal Claim covers the observed boundary events for a rebuild with
one trigger. It defines the allowed order and outcomes of those events.

The lifecycle projection profile covers writes with a recorded outcome and
a Worker carrier delta. It requires the selected base before the write
and reports the recorded write outcome after projection succeeds or
Kernel rejects the base or requires reconciliation.

A lost Worker reply leads to an unknown result and a write block.
The blocked-request path ends before Worker dispatch. This trace
covers the block and refusal events for individual requests.

For successful startup catch-up, attach the watcher before capture. Wait
for completed capture and a completed watcher observation in either order.
Verify Kernel admission of Current and Draft before confirming live catch-up.
With changed Current or Draft carriers at Incremental Startup, observe
the accepted checkpoint proof from Database Server C71.
This profile is separate from `generate`; Archive, exact Project and
generation values, wire transport, and error branches remain outside it.
Their absence from this profile does not exclude them from startup.

### Formal Claim

```python
component_workflow(
    component="C68",
    action="generate",
    machine={
        "id": "orchestrator_rebuild",
        "initial": "idle",
        "states": {
            "idle": {"on": {
                "rebuild_request": {"target": "clear_proof", "guard": {
                    "type": "matchesTrace", "params": {"kind": "trigger", "target": "jobs",
                        "detail": {"route": "POST /jobs/build", "transport": "http",
                                   "operation": "generate"}}}},
            }},
            "clear_proof": {"on": {
                "generation_reuse_write": {"target": "start_worker", "guard": {
                    "type": "matchesTrace", "params": {
                        "kind": "effect", "target": "C68.generation_reuse",
                        "outcome": "succeeded", "detail": {"state": "cleared"}}}},
            }},
            "start_worker": {"on": {
                "worker_started": [
                    {"target": "await_worker", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "effect", "target": "C69", "outcome": "succeeded",
                            "detail": {"interface": "atom_snapshot", "transport": "cli",
                                       "runner": "managed_python",
                                       "module": "WORKERS_beta_C69.WORKERS_beta_C69__shared",
                                       "parent_env": "ANECHOIC_BETA_WORKER_PARENT_PID"}}}},
                    {"target": "report_failure", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "effect", "target": "C69", "outcome": "failed"}}},
                ],
            }},
            "await_worker": {"on": {
                "worker_snapshot_received": {"target": "admit_snapshot", "guard": {
                    "type": "matchesTrace", "params": {
                        "kind": "effect", "target": "C69.artifacts", "outcome": "sealed",
                        "detail": {"component": "C69", "action": "atom_snapshot", "output": "succeeded"}}}},
                "generation_result": [
                    {"target": "failed", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "output", "outcome": "failed",
                            "detail": {"code": "generation_failed"}}}},
                    {"target": "aborted", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "output", "outcome": "aborted",
                            "detail": {"code": "worker_aborted"}}}},
                ],
            }},
            "admit_snapshot": {"on": {
                "generation_admission_requested": {"target": "await_commit", "guard": {
                    "type": "matchesTrace", "params": {
                        "kind": "effect", "target": "C71", "outcome": "requested",
                        "detail": {"interface": "database_api", "transport": "http",
                                   "route": "admit", "operation": "PUT /generation"}}}},
                "generation_result": [
                    {"target": "failed", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "output", "outcome": "failed",
                            "detail": {"code": "generation_failed"}}}},
                    {"target": "aborted", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "output", "outcome": "aborted",
                            "detail": {"code": "worker_aborted"}}}},
                ],
            }},
            "await_commit": {"on": {
                "generation_committed": {"target": "await_admission_outcome", "guard": {
                    "type": "matchesTrace", "params": {
                        "kind": "effect", "target": "C71.generation", "outcome": "committed",
                        "detail": {"component": "C71", "action": "beta_full_generation_admission",
                                   "output": "succeeded"}}}},
                "generation_admission_failed": {"target": "report_failure", "guard": {
                    "type": "matchesTrace", "params": {
                        "kind": "effect", "target": "C71.previous_generation", "outcome": "retained",
                        "detail": {"component": "C71", "action": "beta_full_generation_admission",
                                   "output": "failed"}}}},
                "generation_result": [
                    {"target": "failed", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "output", "outcome": "failed",
                            "detail": {"code": "generation_failed"}}}},
                    {"target": "aborted", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "output", "outcome": "aborted",
                            "detail": {"code": "worker_aborted"}}}},
                ],
            }},
            "await_admission_outcome": {"on": {
                "generation_admission": [
                    {"target": "store_proof", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "effect", "target": "C71", "outcome": "succeeded",
                            "detail": {"reuse_proof_present": True}}}},
                    {"target": "return_replacement_ids", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "effect", "target": "C71", "outcome": "succeeded",
                            "detail": {"reuse_proof_present": False}}}},
                ],
                "generation_result": {"target": "failed", "guard": {
                    "type": "matchesTrace", "params": {
                        "kind": "output", "outcome": "failed",
                        "detail": {"code": "generation_failed"}}}},
            }},
            "store_proof": {"on": {
                "generation_reuse_write": {"target": "return_replacement_ids", "guard": {
                    "type": "matchesTrace", "params": {
                        "kind": "effect", "target": "C68.generation_reuse",
                        "outcome": "succeeded", "detail": {"state": "stored"}}}},
            }},
            "return_replacement_ids": {"on": {
                "replacement_ids_returned": {"target": "report_success", "guard": {
                    "type": "matchesTrace", "params": {
                        "kind": "effect", "target": "C68.replacement_ids", "outcome": "returned"}}},
            }},
            "report_success": {"on": {
                "generation_result": {"target": "succeeded", "guard": {
                    "type": "matchesTrace", "params": {
                        "kind": "output", "outcome": "succeeded", "detail": {"kind": "full"}}}},
            }},
            "report_failure": {"on": {
                "generation_result": {"target": "failed", "guard": {
                    "type": "matchesTrace", "params": {
                        "kind": "output", "outcome": "failed",
                        "detail": {"code": "generation_failed"}}}},
            }},
            "succeeded": {"type": "final"},
            "failed": {"type": "final"},
            "aborted": {"type": "final"},
        },
    },
)
```


```python
component_workflow(
    component='C68',
    action='beta_lifecycle_delta_projection',
    machine={
        'id': 'c68_beta_lifecycle_delta_projection',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'lifecycle_requested': {'target': 'selecting_base', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'jobs',
                        'detail': {
                            'route': 'POST /jobs/lifecycle',
                            'transport': 'http',
                            'operation': 'lifecycle',
                        },
                    },
                }},
            }},
            'selecting_base': {'on': {
                'lifecycle_base_selected': {'target': 'dispatching_write', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C68.admitted_base', 'outcome': 'selected',
                    },
                }},
                'lifecycle_gate_already_blocked': {'target': 'refusing_blocked', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C68.write_gate', 'outcome': 'blocked',
                    },
                }},
            }},
            'awaiting_write': {'on': {
                'lifecycle_worker_reply_lost': {'target': 'blocking_writes', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C69.write_reply', 'outcome': 'missing',
                    },
                }},
                'lifecycle_worker_delta_received': {'target': 'recording_write', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C69.lifecycle_result', 'outcome': 'outcome_and_delta_returned',
                        'detail': {
                            'component': 'C69',
                            'action': 'worker_ticket_lifecycle',
                            'output': 'delta_returned',
                        },
                    },
                }},
                'lifecycle_worker_projection_error_received': {'target': 'reporting_worker_projection_error', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C69.projection_error', 'outcome': 'reported',
                        'detail': {
                            'component': 'C69',
                            'action': 'worker_ticket_lifecycle',
                            'output': 'projection_failed',
                        },
                    },
                }},
            }},
            'submitting_delta': {'on': {
                'lifecycle_delta_requested': {'target': 'awaiting_delta', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C71', 'outcome': 'delta_requested',
                        'detail': {
                            'interface': 'database_api',
                            'route': 'admit_native_delta',
                            'transport': 'http',
                            'operation': 'PUT /generation/native-delta',
                        },
                    },
                }},
            }},
            'awaiting_delta': {'on': {
                'lifecycle_delta_committed': {'target': 'reporting_success', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C71.delta', 'outcome': 'committed',
                        'detail': {
                            'component': 'C71',
                            'action': 'beta_native_delta_admission',
                            'output': 'admitted',
                        },
                    },
                }},
                'lifecycle_delta_stale_base': {'target': 'reporting_rejection', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C71.previous_generation', 'outcome': 'retained',
                        'detail': {
                            'component': 'C71',
                            'action': 'beta_native_delta_admission',
                            'output': 'stale_base',
                        },
                    },
                }},
                'lifecycle_delta_reconcile': {'target': 'reporting_rejection', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C71.previous_generation', 'outcome': 'retained',
                        'detail': {
                            'component': 'C71',
                            'action': 'beta_native_delta_admission',
                            'output': 'reconciliation_required',
                        },
                    },
                }},
            }},
            'reporting_success': {'on': {
                'lifecycle_write_reported': {'target': 'success_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C68.write_outcome', 'outcome': 'reported',
                    },
                }},
            }},
            'reporting_rejection': {'on': {
                'lifecycle_write_reported': {'target': 'rejection_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C68.write_outcome', 'outcome': 'reported',
                    },
                }},
            }},
            'success_response': {'on': {
                'lifecycle_projected': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'projected',
                    },
                }},
            }},
            'rejection_response': {'on': {
                'lifecycle_projection_rejected': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'projection_rejected',
                    },
                }},
            }},
            'done': {'type': 'final'},
            'dispatching_write': {'on': {
                'lifecycle_write_dispatched': {'target': 'awaiting_write', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C69.lifecycle_dispatch', 'outcome': 'requested',
                    },
                }},
            }},
            'blocking_writes': {'on': {
                'lifecycle_block_later_writes': {'target': 'reporting_unknown', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C68.write_gate', 'outcome': 'blocked',
                    },
                }},
            }},
            'reporting_unknown': {'on': {
                'lifecycle_write_outcome_unknown': {'target': 'unknown_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C68.write_outcome', 'outcome': 'unknown',
                    },
                }},
            }},
            'unknown_response': {'on': {
                'lifecycle_unknown_result': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'write_unknown',
                    },
                }},
            }},
            'refusing_blocked': {'on': {
                'lifecycle_refuse_dispatch': {'target': 'blocked_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C68.write_request', 'outcome': 'rejected',
                    },
                }},
            }},
            'blocked_response': {'on': {
                'lifecycle_blocked_result': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'write_blocked',
                    },
                }},
            }},
            'recording_write': {'on': {
                'lifecycle_write_recorded': {'target': 'submitting_delta', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C68.write_outcome', 'outcome': 'recorded',
                    },
                }},
            }},
            'reporting_worker_projection_error': {'on': {
                'lifecycle_worker_projection_error_reported': {'target': 'worker_projection_error_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C68.worker_projection_error', 'outcome': 'reported',
                    },
                }},
            }},
            'worker_projection_error_response': {'on': {
                'lifecycle_worker_projection_failed': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'worker_projection_failed',
                    },
                }},
            }},
        },
    },
)
```

```python
component_workflow(
    component='C68',
    action='beta_startup_catch_up',
    machine={
        'id': 'c68_beta_startup_catch_up',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'startup_requested': {'target': 'attaching_watcher', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'attaching_watcher': {'on': {
                'startup_watcher_attached': {'target': 'awaiting_capture_start_or_observation', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C68.source_watcher', 'outcome': 'attached'}}},
            }},
            'awaiting_capture_start_or_observation': {'on': {
                'startup_capture_started': {'target': 'awaiting_evidence', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C68.startup_capture', 'outcome': 'started'}}},
                'startup_observation_completed': {'target': 'awaiting_capture_start', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C68.watcher_observation', 'outcome': 'completed'}}},
            }},
            'awaiting_capture_start': {'on': {
                'startup_capture_started': {'target': 'awaiting_capture', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C68.startup_capture', 'outcome': 'started'}}},
            }},
            'awaiting_evidence': {'on': {
                'startup_capture_completed': {'target': 'awaiting_observation', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C68.startup_capture', 'outcome': 'completed'}}},
                'startup_observation_completed': {'target': 'awaiting_capture', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C68.watcher_observation', 'outcome': 'completed'}}},
            }},
            'awaiting_observation': {'on': {
                'startup_observation_completed': {'target': 'verifying_admission', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C68.watcher_observation', 'outcome': 'completed'}}},
            }},
            'awaiting_capture': {'on': {
                'startup_capture_completed': {'target': 'verifying_admission', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C68.startup_capture', 'outcome': 'completed'}}},
            }},
            'verifying_admission': {'on': {
                'startup_checkpoint_admission_verified': {'target': 'confirming', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'startup_current_and_draft_admission', 'outcome': 'verified',
                        'detail': {'component': 'C71', 'action': 'beta_startup_checkpoint_admission',
                                   'output': 'checkpoint_admitted', 'startup_case': 'incremental_changed'},
                    },
                }},
                'startup_other_admission_verified': {'target': 'confirming', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'startup_current_and_draft_admission', 'outcome': 'verified',
                        'detail': {'startup_case': 'other'},
                    },
                }},
            }},
            'confirming': {'on': {
                'startup_live_catch_up_confirmed': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'current_and_draft', 'outcome': 'catch_up_confirmed'}}},
            }},
            'reporting': {'on': {
                'startup_catch_up_returned': {'target': 'confirmed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'live_catch_up_confirmed'}}},
            }},
            'confirmed': {'type': 'final'},
        },
    },
)
```

## Details

Use the Engine Python environment and set
`PYTHONPATH=LAYER_4_ENGINE_STUDIO_C14`. Keep `lean` on the executable
path for trace checking.

Run `python -m IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.workflow_spec`
with this Atom path and `render` to write Mermaid. Use `check <matrix.json>`
to check a run. Export one run from `flow_events` as a Workbench JSON matrix
with all columns and order the rows by `sequence`.

The check reports `matched`, `different`, or `unresolved`. A run needs a
recorded rebuild trigger, a terminal output, and a complete event sequence.
Use the archived revision for traces recorded before admission included
`reuse_proof_present`.
