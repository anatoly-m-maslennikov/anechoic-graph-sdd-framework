---
atom_family: SPEC
atom_id: AN-S-5022
concern:
  subject: "Model"
  path: "ANECHOIC"
  relation: "is_contained_by"
container:
  component: C75
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3395@6
state:
  status: archived
  version: 8
  updated_at: "2026-11-27T16:19:44.298791+00:00"
---
## Summary

Prepare Spec Engine from runtime assets and ingested Specs

## Claim

### Prose Claim

Resolve the compiled Model through the existing admitted asset reader.
Use the image Model when the Project asset cannot be admitted, and report
that fallback. Ingestion stages the Project Spec rows in DuckDB before the
compiler consumes them. Build Model and Structure from the staged snapshot.
Keep the descriptor and Model that pass C53 admission and the
Structure check. Apply the same handoff to a reused, compiled, or
fallback Model. A failed provisional Model does not bind the ready
candidate. Bind the Model fingerprint used by C93 and the digest of
the descriptor that C53 opened. Return those identities and the
same staged snapshot ID. Verification and generation use their
Components with the selected source pins.

### Formal Claim

```python
component_workflow(component='C75', action='prepare_spec_engine', machine={
    'id': 'c75_prepare_spec_engine', 'initial': 'bootstrap', 'states': {
        'bootstrap': {'on': {
            'receipt': {'to': 'ingestion', 'expect': {'kind': 'effect',
                'target': 'C75.bootstrap_model', 'outcome': 'selected', 'detail': {'source': 'receipt'}}},
            'refused': {'to': 'bundled', 'expect': {'kind': 'effect',
                'target': 'C75.bootstrap_fallback', 'outcome': 'reported'}},
            'error': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'bundled': {'on': {
            'selected': {'to': 'ingestion', 'expect': {'kind': 'effect',
                'target': 'C75.bootstrap_model', 'outcome': 'selected', 'detail': {'source': 'bundled'}}},
            'error': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'ingestion': {'on': {
            'read_snapshot': {'to': 'model', 'expect': {'kind': 'effect', 'detail': {'component': 'C95', 'action': 'read_spec_snapshot', 'output': 'ready', 'manifest': 'AN-S-5021@3'}, 'target': 'C95.source_snapshot', 'outcome': 'ready', 'bind': {'snapshot': 'snapshot_id'}}},
            'error': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'model': {'on': {
            'success': {'to': 'structure', 'expect': {'kind': 'effect', 'target': 'C75.model_inputs', 'outcome': 'admitted', 'same_as': {'snapshot_id': 'snapshot'}}},
            'error': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'structure': {'on': {
            'bind_rows': {'to': 'compile', 'expect': {'kind': 'effect',
                'target': 'C75.structure_inputs', 'outcome': 'admitted',
                'same_as': {'snapshot_id': 'snapshot'},
                'bind': {'selected_model': 'model_sha256',
                         'selected_descriptor': 'model_descriptor_sha256'}}},
        }},
        'compile': {'on': {
            'compile_structure': {'to': 'candidate', 'expect': {'kind': 'effect', 'detail': {'component': 'C93', 'action': 'compile_pinned_structure', 'output': 'succeeded', 'manifest': 'AN-S-5018@7', 'interface': 'compile_pinned_structure', 'transport': 'in_process'}, 'target': 'C93.structure_snapshot', 'outcome': 'ready',
                'same_as': {'model_sha256': 'selected_model'}}},
            'error': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'candidate': {'on': {
            'success': {'to': 'return', 'expect': {'kind': 'effect', 'target': 'C75.compiled_candidate', 'outcome': 'ready'}},
            'error': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'return': {'on': {'result': {'to': 'end', 'expect': {
            'kind': 'output', 'outcome': 'ready',
            'same_as': {'snapshot_id': 'snapshot',
                        'model_sha256': 'selected_model',
                        'model_descriptor_sha256': 'selected_descriptor'}}}}},
        'end': {'type': 'final'},
    },
})
```

```python
component_workflow(component='C75', action='verify_formal_chain', machine={
    'id': 'c75_verify_formal_chain', 'initial': 'verify', 'states': {
        'verify': {'on': {
            'verify_specs': {'to': 'return', 'expect': {'kind': 'effect', 'detail': {'component': 'C94', 'action': 'verify_pinned_specs', 'output': 'compared', 'manifest': 'AN-S-5020@5'}, 'target': 'C94.formal_verification', 'outcome': 'compared'}},
            'error': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'incomplete'}},
        }},
        'return': {'on': {'result': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'compared'}}}},
        'end': {'type': 'final'},
    },
})
```

```python
component_workflow(component='C75', action='generate_framing_cases', machine={
    'id': 'c75_generate_framing_cases', 'initial': 'generate', 'states': {
        'generate': {'on': {
            'generate_cases': {'to': 'return', 'expect': {'kind': 'effect', 'detail': {'component': 'C94', 'action': 'generate_pinned_cases', 'output': 'generated', 'manifest': 'AN-S-5020@5'}, 'target': 'C94.generated_cases', 'outcome': 'ready'}},
            'error': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'invalid'}},
        }},
        'return': {'on': {'result': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'generated'}}}},
        'end': {'type': 'final'},
    },
})
```

```python
component_workflow(component='C75', action='select_bootstrap_model', machine={
    'id': 'c75_select_bootstrap_model', 'initial': 'admit', 'states': {
        'admit': {'on': {
            'receipt': {'to': 'receipt_ready', 'expect': {'kind': 'effect',
                'target': 'C75.bootstrap_model', 'outcome': 'selected', 'detail': {'source': 'receipt'}}},
            'refused': {'to': 'bundled', 'expect': {'kind': 'effect',
                'target': 'C75.bootstrap_fallback', 'outcome': 'reported'}},
            'error': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'bundled': {'on': {
            'selected': {'to': 'bundled_ready', 'expect': {'kind': 'effect',
                'target': 'C75.bootstrap_model', 'outcome': 'selected', 'detail': {'source': 'bundled'}}},
            'error': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'receipt_ready': {'on': {'result': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'receipt'}}}},
        'bundled_ready': {'on': {'result': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'bundled'}}}},
        'end': {'type': 'final'},
    },
})
```

```python
component_workflow(component='C75', action='compile_workflow', machine={
    'id': 'c75_compile_workflow', 'initial': 'normalize', 'states': {
        'normalize': {'on': {
            'model_ready': {'to': 'render', 'expect': {'kind': 'effect',
                'target': 'C75.workflow_model', 'outcome': 'normalized',
                'bind': {'workflow': 'model'}}},
            'error': {'to': 'end', 'expect': {'kind': 'output',
                'outcome': 'invalid'}},
        }},
        'render': {'on': {
            'diagram_ready': {'to': 'return', 'expect': {'kind': 'effect',
                'target': 'C75.workflow_diagram', 'outcome': 'rendered',
                'same_as': {'model': 'workflow'}}},
        }},
        'return': {'on': {
            'result': {'to': 'end', 'expect': {'kind': 'output',
                'outcome': 'compiled', 'same_as': {'model': 'workflow'}}},
        }},
        'end': {'type': 'final'},
    },
})
```
