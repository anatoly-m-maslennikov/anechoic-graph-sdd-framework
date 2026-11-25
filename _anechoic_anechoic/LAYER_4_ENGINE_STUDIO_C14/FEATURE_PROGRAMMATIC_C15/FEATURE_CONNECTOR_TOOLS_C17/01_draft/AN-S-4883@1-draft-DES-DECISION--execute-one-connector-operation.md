---
atom_family: SPEC
atom_id: AN-S-4883
container:
  component: C17
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4882@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T00:00:00+00:00'
---

## Summary

Execute one connector operation.

## Claim

### Prose Claim

Admit the request before dispatch. Verify a read, applied delta, or
unchanged result before reporting success. Reject invalid bindings
before dispatch. Return an uncertain effect as a structured error.

### Formal Claim

```python
component_workflow(
    component='C17',
    action='execute_connector_operation',
    machine={
        'id': 'c17_execute_connector_operation',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'operation_requested': {'target': 'validating', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'connector_operation',
                    },
                }},
            }},
            'validating': {'on': {
                'bindings_admitted': {'target': 'deciding', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C17.request', 'outcome': 'admitted',
                    },
                }},
                'invalid_request': {'target': 'reporting_rejection', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C17.request_error', 'outcome': 'reported',
                    },
                }},
            }},
            'deciding': {'on': {
                'read_dispatched': {'target': 'observing_read', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C17.backend_dispatch', 'outcome': 'read',
                    },
                }},
                'write_dispatched': {'target': 'awaiting_write', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C17.backend_dispatch', 'outcome': 'write',
                    },
                }},
                'already_satisfied': {'target': 'observing_no_op', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C17.storage_state', 'outcome': 'verified_unchanged',
                    },
                }},
            }},
            'observing_read': {'on': {
                'read_verified': {'target': 'reporting_read', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C17.operation_result', 'outcome': 'verified',
                    },
                }},
            }},
            'awaiting_write': {'on': {
                'delta_applied': {'target': 'observing_write', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C17.admitted_delta', 'outcome': 'applied',
                    },
                }},
                'uncertain_effect_reported': {'target': 'reporting_uncertainty', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C17.effect_uncertain', 'outcome': 'reported',
                    },
                }},
            }},
            'observing_write': {'on': {
                'write_verified': {'target': 'reporting_write', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C17.operation_result', 'outcome': 'verified',
                    },
                }},
            }},
            'observing_no_op': {'on': {
                'no_op_verified': {'target': 'reporting_no_op', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C17.operation_result', 'outcome': 'verified',
                    },
                }},
            }},
            'reporting_read': {'on': {
                'read_reported': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'read_reported',
                    },
                }},
            }},
            'reporting_write': {'on': {
                'write_reported': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'write_reported',
                    },
                }},
            }},
            'reporting_no_op': {'on': {
                'write_no_op': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'write_no_op',
                    },
                }},
            }},
            'reporting_uncertainty': {'on': {
                'write_uncertain': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'write_uncertain',
                    },
                }},
            }},
            'reporting_rejection': {'on': {
                'request_rejected': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'request_rejected',
                    },
                }},
            }},
            'done': {'type': 'final'},
        },
    },
)
```

## Details

The workflow abstracts the connector backend and the actual result values.
The Contract also defines the separate Subject lookup and known partial
effect handling.
