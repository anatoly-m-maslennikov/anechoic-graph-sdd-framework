---
atom_family: SPEC
atom_id: AN-S-3384
container:
  component: C69
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3336@26-draft
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T00:00:00+00:00'
---

## Summary

Build a pinned generation from an admitted Project binding.

## Claim

### Prose Claim

For cold full generation, a Worker compiles the Model and Structure,
captures the snapshot and graph,
then publishes sealed generation artifacts and returns the generation receipt
with those seals before reporting success. Process start alone is not success.

For one admitted Ticket write with a recorded outcome, capture its
carriers against the selected base and verify the hashes. Return
the outcome and delta after that check. Report a projection error
if capture fails or the hashes fail validation.

### Formal Claim

```python
component_workflow(
    component='C69',
    action='atom_snapshot',
    machine={
        'id': 'c69_beta_worker_build_generation',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'generation_requested': {'target': 'step_1', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'atom_snapshot', 'detail': {
                        'transport': 'cli', 'runner': 'managed_python',
                        'module': 'WORKERS_beta_C69.WORKERS_beta_C69__shared',
                        'arguments': ['optional --generation-dir <empty-directory>'],
                    }}}},
            }},
            'step_1': {'on': {
                'compile_model_and_structure': {'target': 'step_2', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C69.model_structure', 'outcome': 'compiled'}}},
            }},
            'step_2': {'on': {
                'build_graph_and_capture_snapshot': {'target': 'step_3', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C69.snapshot_graph', 'outcome': 'captured'}}},
            }},
            'step_3': {'on': {
                'generation_artifacts_published': {'target': 'returning_receipt', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C69.artifacts', 'outcome': 'sealed'}}},
            }},
            'returning_receipt': {'on': {
                'generation_receipt_returned_with_seals': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C69.receipt', 'outcome': 'returned_with_artifact_seals'}}},
            }},
            'responding': {'on': {
                'generation_receipt_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
        },
    },
)
```


```python
component_workflow(
    component='C69',
    action='worker_ticket_lifecycle',
    machine={
        'id': 'c69_worker_ticket_lifecycle',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'ticket_request': {'target': 'admitting', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'trigger',
                    },
                }},
            }},
            'admitting': {'on': {
                'ticket_request_admitted': {'target': 'executing', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C69.lifecycle_request', 'outcome': 'admitted',
                    },
                }},
            }},
            'executing': {'on': {
                'ticket_outcome_recorded': {'target': 'capturing_delta', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C69.native_write_outcome', 'outcome': 'recorded',
                    },
                }},
            }},
            'capturing_delta': {'on': {
                'affected_carriers_captured': {'target': 'checking_delta', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C69.carrier_delta', 'outcome': 'captured_against_admitted_base',
                    },
                }},
                'capture_failed': {'target': 'reporting_error', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C69.projection_error', 'outcome': 'reported',
                    },
                }},
            }},
            'checking_delta': {'on': {
                'carrier_hashes_verified': {'target': 'returning_delta', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C69.carrier_hashes', 'outcome': 'verified_against_write_receipt',
                    },
                }},
                'carrier_hashes_mismatch': {'target': 'reporting_error', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C69.projection_error', 'outcome': 'reported',
                    },
                }},
            }},
            'returning_delta': {'on': {
                'ticket_outcome_and_delta_returned': {'target': 'reporting_delta', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C69.lifecycle_result', 'outcome': 'outcome_and_delta_returned',
                    },
                }},
            }},
            'reporting_delta': {'on': {
                'ticket_delta_completed': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'delta_returned',
                    },
                }},
            }},
            'reporting_error': {'on': {
                'ticket_projection_failed': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'projection_failed',
                    },
                }},
            }},
            'done': {'type': 'final'},
        },
    },
)
```

## Details

The effect targets and outcomes are formal abstractions of successful generation.

The event names describe an expected sequence; the Worker does not record
them as flow events. Trace conformance requires recorded evidence.
