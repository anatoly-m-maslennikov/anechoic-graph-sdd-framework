---
atom_family: SPEC
atom_id: AN-S-3386
container:
  component: C71
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3335@32-draft
state:
  status: draft
  version: 5
  updated_at: '2026-11-26T20:30:26.177912+00:00'
---
## Summary

Serve a SQL request for the admitted Beta Project generation.

## Claim

### Prose Claim

For a successful new read-only SQL Run, the Database Server checks the
Project binding and accepted generation, admits one read-only SELECT without
external access, then executes and retains the result before returning it.
The result has at most 1,000 rows and 1 MiB of serialized data. Refuse a new
result that would exceed result capacity; do not retain it. A query can also
append to history.

For a Model or Structure request, the Server checks the Project binding and
pairs accepted content with its corresponding generation ID before returning
it. For the Structure-specific outcome, the Server renders canonical Structure
from accepted rows and generation facts before pairing it with its generation
ID. A bound Model request can return the accepted file with an empty
generation header when no generation is admitted. Structure requires an admitted generation.
Reject a foreign instance.

For full generation admission, the Server checks the Project binding and
verifies admission inputs before it commits paired artifacts and the Project
snapshot, including the enabled Realization Graph where relevant, in one
transaction. On validation or admission failure before commit it retains the
prior generation. A foreign instance cannot commit a generation.

After commit, the Server makes the Model asset available with the exact
descriptor digest from the verified admission receipt.
It initializes the asset on the first fallback and skips a write when the
bytes already match. If publication fails, it invalidates the generation
receipt, retains the previous file, and reports failure.

The carrier delta profile checks the Project binding and named base
before admission. One commit publishes the changed Atom and Model-defined
relation rows with their graph rows and Current Lens membership. The
accepted Model, Structure, and Realization Graph stay in place. A stale
base or a delta that cannot preserve relation ownership leaves the
previous projection in place.

For Incremental Startup with changed Current and Draft carriers, the Server
confirms the named base. It commits affected rows and checkpoints together,
including removal of checkpoints for absent paths and old move paths. It makes
the current proof available to C68 before verification is reported.

### Formal Claim

```python
component_workflow(
    component='C71',
    action='beta_database_query',
    machine={
        'id': 'c71_beta_database_query',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'database_request_received': {'target': 'step_1', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'database_api',
                     'detail': {'route': 'query', 'transport': 'http', 'operation': 'POST /database'}}}},
            }},
            'step_1': {'on': {
                'admitted_generation_read': {'target': 'step_2', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71', 'outcome': 'generation_checked'}}},
            }},
            'step_2': {'on': {
                'read_only_select_admitted': {'target': 'step_3', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71', 'outcome': 'read_only_select_admitted'}}},
            }},
            'step_3': {'on': {
                'result_capacity_exceeded': {'target': 'reporting_refusal', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71.result_capacity', 'outcome': 'exceeded'}}},
                'query_executed_and_retained': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71.query_result', 'outcome': 'query_retained',
                     'detail': {'rows': {'at_most': 1000}, 'serialized_bytes': {'at_most': 1048576}}}}},
            }},
            'reporting_refusal': {'on': {
                'capacity_refusal_reported': {'target': 'refused', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'result_capacity_exceeded'}}},
            }},
            'refused': {'type': 'final'},
            'responding': {'on': {
                'query_result_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
        },
    },
)
```

```python
component_workflow(
    component='C71',
    action='beta_database_artifact_read',
    machine={
        'id': 'c71_beta_database_artifact_read',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'model_requested': {'target': 'checking_instance', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'database_api',
                     'detail': {'route': 'model', 'transport': 'http', 'operation': 'GET /model'}}}},
                'structure_requested': {'target': 'checking_structure_instance', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'database_api',
                     'detail': {'route': 'structure', 'transport': 'http', 'operation': 'GET /structure'}}}},
            }},
            'checking_instance': {'on': {
                'binding_matched': {'target': 'reading', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'project_binding', 'outcome': 'matched'}}},
                'foreign_instance': {'target': 'rejected', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'foreign_instance'}}},
            }},
            'checking_structure_instance': {'on': {
                'structure_binding_matched': {'target': 'reading_structure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'project_binding', 'outcome': 'matched'}}},
                'structure_foreign_instance': {'target': 'rejected', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'foreign_instance'}}},
            }},
            'reading_structure': {'on': {
                'structure_rendered': {'target': 'pairing_structure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'structure', 'outcome': 'rendered_from_accepted_rows'}}},
                'structure_no_generation': {'target': 'rejected', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'no_generation'}}},
            }},
            'pairing_structure': {'on': {
                'rendered_structure_and_generation_paired': {'target': 'responding_structure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'artifact_content_generation', 'outcome': 'paired'}}},
            }},
            'responding_structure': {'on': {
                'structure_artifact_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
                'structure_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'structure_returned'}}},
            }},
            'reading': {'on': {
                'content_and_generation_paired': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'artifact_content_generation', 'outcome': 'paired'}}},
                'standalone_model_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded', 'detail': {'generation_id': ''}}}},
                'no_generation': {'target': 'rejected', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'no_generation'}}},
            }},
            'responding': {'on': {
                'artifact_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
            'rejected': {'type': 'final'},
        },
    },
)
```


```python
component_workflow(
    component='C71',
    action='beta_full_generation_admission',
    machine={
        'id': 'c71_beta_full_generation_admission',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'generation_requested': {'target': 'checking_instance', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'database_api',
                     'detail': {'route': 'admit', 'transport': 'http', 'operation': 'PUT /generation'}}}},
            }},
            'checking_instance': {'on': {
                'binding_matched': {'target': 'verifying', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71.project_binding', 'outcome': 'matched'}}},
                'foreign_instance': {'target': 'rejected', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'foreign_instance'}}},
            }},
            'verifying': {'on': {
                'inputs_verified': {'target': 'committing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71.admission_inputs', 'outcome': 'verified',
                     'bind': {'descriptor': 'model_descriptor_sha256'}}}},
                'validation_failed': {'target': 'failed_response', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71.previous_generation', 'outcome': 'retained'}}},
            }},
            'committing': {'on': {
                'generation_committed': {'target': 'ensuring_asset', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71.generation', 'outcome': 'committed'}}},
                'admission_failed': {'target': 'failed_response', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71.previous_generation', 'outcome': 'retained'}}},
            }},
            'ensuring_asset': {'on': {
                'asset_available': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71.accepted_model_asset', 'outcome': 'available',
                     'same_as': {'model_descriptor_sha256': 'descriptor'}}}},
                'publication_failed': {'target': 'invalidating_receipt', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71.accepted_model_asset', 'outcome': 'publication_failed'}}},
            }},
            'invalidating_receipt': {'on': {
                'receipt_invalidated': {'target': 'failed_response', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71.generation_receipt', 'outcome': 'invalidated'}}},
            }},
            'responding': {'on': {
                'admission_succeeded': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'failed_response': {'on': {
                'admission_failed': {'target': 'rejected', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'succeeded': {'type': 'final'},
            'rejected': {'type': 'final'},
        },
    },
)
```


```python
component_workflow(
    component='C71',
    action='beta_native_delta_admission',
    machine={
        'id': 'c71_beta_native_delta_admission',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'native_delta_requested': {'target': 'checking_binding', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'database_api',
                        'detail': {
                            'route': 'admit_native_delta',
                            'transport': 'http',
                            'operation': 'PUT /generation/native-delta',
                        },
                    },
                }},
            }},
            'checking_binding': {'on': {
                'delta_binding_matched': {'target': 'checking_base', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C71.project_binding', 'outcome': 'matched',
                    },
                }},
                'delta_foreign_instance': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'foreign_instance',
                    },
                }},
            }},
            'checking_base': {'on': {
                'delta_base_matched': {'target': 'checking_relations', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C71.base_generation', 'outcome': 'matched',
                    },
                }},
                'delta_base_stale': {'target': 'retaining_stale_base', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C71.base_generation', 'outcome': 'stale',
                    },
                }},
            }},
            'checking_relations': {'on': {
                'delta_relations_preserved': {'target': 'committing', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C71.relation_ownership', 'outcome': 'preserved',
                    },
                }},
                'delta_reconciliation_required': {'target': 'retaining_for_reconciliation', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C71.reconciliation', 'outcome': 'required',
                    },
                }},
            }},
            'committing': {'on': {
                'native_delta_committed': {'target': 'preserving_artifacts', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C71.delta', 'outcome': 'committed',
                    },
                }},
            }},
            'preserving_artifacts': {'on': {
                'delta_artifacts_retained': {'target': 'success_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C71.model_structure_realization_graph', 'outcome': 'retained',
                    },
                }},
            }},
            'retaining_stale_base': {'on': {
                'delta_stale_base_retained': {'target': 'stale_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C71.previous_generation', 'outcome': 'retained',
                    },
                }},
            }},
            'retaining_for_reconciliation': {'on': {
                'delta_reconcile_base_retained': {'target': 'reconcile_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C71.previous_generation', 'outcome': 'retained',
                    },
                }},
            }},
            'success_response': {'on': {
                'delta_admitted': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'admitted',
                    },
                }},
            }},
            'stale_response': {'on': {
                'delta_stale_rejected': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'stale_base',
                    },
                }},
            }},
            'reconcile_response': {'on': {
                'delta_reconciliation_reported': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'reconciliation_required',
                    },
                }},
            }},
            'done': {'type': 'final'},
        },
    },
)
```

```python
component_workflow(
    component='C71',
    action='beta_startup_checkpoint_admission',
    machine={
        'id': 'c71_beta_startup_checkpoint_admission',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'incremental_startup_received': {'target': 'confirming_base', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'confirming_base': {'on': {
                'base_confirmed': {'target': 'committing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71.startup_base', 'outcome': 'confirmed'}}},
            }},
            'committing': {'on': {
                'rows_and_checkpoints_committed': {'target': 'exposing_proof', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71.startup_rows_and_checkpoints', 'outcome': 'committed'}}},
            }},
            'exposing_proof': {'on': {
                'proof_available': {'target': 'verifying', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71.startup_proof', 'outcome': 'available'}}},
            }},
            'verifying': {'on': {
                'admission_verified': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'startup_current_and_draft_admission', 'outcome': 'verified'}}},
            }},
            'responding': {'on': {
                'checkpoint_admitted': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'checkpoint_admitted'}}},
            }},
            'succeeded': {'type': 'final'},
        },
    },
)
```

## Details

The SQL profile covers a new Run. The checkpoint profile covers Incremental
Startup with changed Current and Draft carriers. Paging, other failures, other
checkpoint cases, and Archive remain outside these profiles.

The Contract describes Structure JSON reconstructed from accepted rows.
AN-S-4797@1 describes accepted artifact bytes, and AN-S-4798@1 describes
a Host read under a lock. Resolve these accounts and the read sequence before
activation. This workflow does not choose a representation or prescribe a lock.
