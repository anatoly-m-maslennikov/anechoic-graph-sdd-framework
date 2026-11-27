---
atom_family: SPEC
atom_id: AN-S-5053
container:
  component: C15
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3045@29-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T10:55:20+00:00'
---

## Summary

Compile Python Model Claim fences

## Claim

### Prose Claim

Select Python fences under Claim and Formal Claim, except matching typed
properties when the skip option is set. Compile them in source order.
Return one block per selected fence after all compilation finishes. Join
the statements in each block with a semicolon and newline. Zero
statements produce an empty block. No selected fences produce no blocks.
Propagate a compilation error and discard the partial result.

### Formal Claim

```python
component_workflow(component='C15', action='compile_formal_claim', machine={
    'id': 'compile_formal_claim', 'initial': 'idle', 'states': {
        'idle': {'on': {'body': {'expect': {'kind': 'trigger'}, 'to': 'select'}}},
        'select': {'on': {
            'no_selected_python': {'expect': {'kind': 'output', 'outcome': 'no_statements'}, 'to': 'done'},
            'python': {'expect': {'kind': 'effect', 'target': 'C15.claim_fences',
                                  'outcome': 'python_selected'}, 'to': 'compile'},
        }},
        'compile': {'on': {
            'compiled': {'expect': {'kind': 'effect', 'target': 'C15.model_statements',
                                    'outcome': 'compiled'}, 'to': 'return_statements'},
            'compiled_empty': {'expect': {'kind': 'effect', 'target': 'C15.model_statements',
                                          'outcome': 'compiled'}, 'to': 'return_empty_blocks'},
            'failed': {'expect': {'kind': 'effect', 'target': 'C15.compilation_error',
                                  'outcome': 'reported'}, 'to': 'report_error'},
        }},
        'return_statements': {'on': {
            'return': {'expect': {'kind': 'output', 'outcome': 'python_statements_returned'}, 'to': 'done'},
        }},
        'return_empty_blocks': {'on': {
            'return': {'expect': {'kind': 'output', 'outcome': 'empty_blocks_returned'}, 'to': 'done'},
        }},
        'report_error': {'on': {
            'report': {'expect': {'kind': 'output', 'outcome': 'compilation_error'}, 'to': 'done'},
        }},
        'done': {'type': 'final'},
    },
})
```
