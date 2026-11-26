---
atom_family: SPEC
atom_id: AN-S-3385
container:
  component: C70
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3340@28-draft
state:
  status: draft
  version: 4
  updated_at: "2026-11-25T10:58:29.166498+00:00"
---
## Summary

Forward a projection rebuild for an admitted Project.

## Claim

### Prose Claim

For an `all` or projection table target, the Backend validates the target,
asks the Project Orchestrator to build, and returns replacement result IDs.
For result and flow-history targets, it forwards the rebuild to Kernel.

A shared Backend Tool call binds the Project, checks the enabled Tool
definition, dispatches the call, and returns the raw Tool result. It
returns a failure if binding, validation, dispatch, or response handling fails.
A failure after dispatch does not establish the Tool's write outcome.

For a shared Ticket Tool call, distinguish an unknown write outcome, a
known write with a projection failure, and a request refused while the
Orchestrator has blocked writes. Preserve the Orchestrator outcome.

A Worker projection error received from Orchestrator is reported as a
projection failure. The error alone leaves the file effects unspecified.

### Formal Claim

```python
component_workflow(
    component='C70',
    action='beta_backend_rebuild_projection',
    machine={
        'id': 'c70_beta_backend_rebuild_projection',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'rebuild_requested': {'target': 'step_1', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'step_1': {'on': {
                'validate_target_and_forward_build': {'target': 'step_2', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C68', 'outcome': 'requested',
                     'detail': {'interface': 'jobs', 'transport': 'http', 'route': 'POST /jobs/build'}}}},
            }},
            'step_2': {'on': {
                'return_replacement_ids': {'target': 'step_3', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C68.replacement_ids', 'outcome': 'returned'}}},
            }},
            'step_3': {'on': {
                'rebuild_result': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
        },
    },
)
```

```python
component_workflow(
    component='C70',
    action='beta_backend_tool_call',
    machine={
        'id': 'c70_beta_backend_tool_call',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'tool_call_requested': {'target': 'binding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'shared_workbench_api',
                     'detail': {'transport': 'http', 'route': 'POST /tools', 'operation': 'tool_call'}}}},
            }},
            'binding': {'on': {
                'project_admitted': {'target': 'validating', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C70.project_binding', 'outcome': 'admitted'}}},
                'tool_call_failed': {'target': 'reporting_tool_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C70.tool_call_failure', 'outcome': 'reported'}}},
            }},
            'validating': {'on': {
                'tool_validated': {'target': 'dispatching', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C70.tool_validation', 'outcome': 'validated'}}},
                'tool_call_failed': {'target': 'reporting_tool_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C70.tool_call_failure', 'outcome': 'reported'}}},
            }},
            'dispatching': {'on': {
                'tool_dispatched': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C70.tool_dispatch', 'outcome': 'dispatched'}}},
                'tool_call_failed': {'target': 'reporting_tool_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C70.tool_call_failure', 'outcome': 'reported'}}},
            }},
            'responding': {'on': {
                'raw_tool_result_returned': {'target': 'returning', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C70.raw_tool_result', 'outcome': 'returned'}}},
                'tool_call_failed': {'target': 'reporting_tool_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C70.tool_call_failure', 'outcome': 'reported'}}},
            }},
            'reporting_tool_failure': {'on': {
                'failure_returned': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'returning': {'on': {
                'tool_call_succeeded': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
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
    component='C70',
    action='beta_backend_lifecycle_failures',
    machine={
        'id': 'c70_beta_backend_lifecycle_failures',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'lifecycle_tool_requested': {'target': 'admitting', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'shared_workbench_api',
                        'detail': {
                            'route': 'POST /tools',
                            'transport': 'http',
                            'operation': 'tool_call',
                        },
                    },
                }},
            }},
            'admitting': {'on': {
                'lifecycle_tool_project_admitted': {'target': 'validating', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C70.project_binding', 'outcome': 'admitted',
                    },
                }},
            }},
            'validating': {'on': {
                'lifecycle_tool_validated': {'target': 'forwarding', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C70.tool_validation', 'outcome': 'validated',
                    },
                }},
            }},
            'forwarding': {'on': {
                'lifecycle_tool_forwarded': {'target': 'awaiting_orchestrator', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C68', 'outcome': 'lifecycle_requested',
                        'detail': {
                            'interface': 'jobs',
                            'route': 'POST /jobs/lifecycle',
                            'transport': 'http',
                            'operation': 'lifecycle',
                        },
                    },
                }},
            }},
            'awaiting_orchestrator': {'on': {
                'orchestrator_write_unknown': {'target': 'reporting_unknown', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C68.write_outcome', 'outcome': 'unknown',
                        'detail': {
                            'component': 'C68',
                            'action': 'beta_lifecycle_delta_projection',
                            'output': 'write_unknown',
                        },
                    },
                }},
                'orchestrator_projection_rejected': {'target': 'reporting_known', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C68.write_outcome', 'outcome': 'reported',
                        'detail': {
                            'component': 'C68',
                            'action': 'beta_lifecycle_delta_projection',
                            'output': 'projection_rejected',
                        },
                    },
                }},
                'orchestrator_worker_projection_failed': {
                    'target': 'reporting_worker_projection_error', 'guard': {
                        'type': 'matchesTrace', 'params': {
                            'kind': 'effect', 'target': 'C68.worker_projection_error', 'outcome': 'reported',
                            'detail': {
                                'component': 'C68',
                                'action': 'beta_lifecycle_delta_projection',
                                'output': 'worker_projection_failed',
                            },
                        },
                    },
                },
                'orchestrator_write_blocked': {'target': 'reporting_refusal', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C68.write_request', 'outcome': 'rejected',
                        'detail': {
                            'component': 'C68',
                            'action': 'beta_lifecycle_delta_projection',
                            'output': 'write_blocked',
                        },
                    },
                }},
            }},
            'reporting_unknown': {'on': {
                'tool_write_outcome_unknown': {'target': 'unknown_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C70.write_outcome', 'outcome': 'unknown',
                    },
                }},
            }},
            'reporting_known': {'on': {
                'tool_write_outcome_known': {'target': 'reporting_projection', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C70.write_outcome', 'outcome': 'known',
                    },
                }},
            }},
            'reporting_projection': {'on': {
                'tool_projection_failure': {'target': 'projection_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C70.projection', 'outcome': 'failed',
                    },
                }},
            }},
            'reporting_worker_projection_error': {'on': {
                'tool_worker_projection_failure': {'target': 'worker_projection_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C70.projection', 'outcome': 'failed',
                    },
                }},
            }},
            'worker_projection_response': {'on': {
                'tool_worker_projection_failure_returned': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'worker_projection_failed',
                    },
                }},
            }},
            'reporting_refusal': {'on': {
                'tool_write_refused': {'target': 'refusal_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C70.write_request', 'outcome': 'rejected',
                    },
                }},
            }},
            'unknown_response': {'on': {
                'tool_unknown_returned': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'write_unknown',
                    },
                }},
            }},
            'projection_response': {'on': {
                'tool_projection_failure_returned': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'projection_rejected',
                    },
                }},
            }},
            'refusal_response': {'on': {
                'tool_refusal_returned': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'write_blocked',
                    },
                }},
            }},
            'done': {'type': 'final'},
        },
    },
)
```

## Details

The rebuild Formal Claim covers the Orchestrator path only. The event names
describe expected sequences; the Backend does not record them as flow events.
Trace conformance requires recorded evidence.
