---
atom_family: SPEC
atom_id: AN-S-4793
container:
  component: C15
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4792@2-draft
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T11:02:11.485674+00:00'
---

## Summary

Compile formal Model Claim blocks

## Claim

### Prose Claim

Classify a formal Claim fence by language. Compile a Python Model Claim or remove comments from CFEL and return its statements. Report a compilation error, or return no Model statements for another language.

The model covers one fence per trace. It does not establish implementation conformance, validate the statements, or define the representation of errors and empty results.

### Formal Claim

```python
component_workflow(
    component='C15',
    action='compile_formal_claim',
    machine={
        'id': 'c15_compile_formal_claim',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'python_claim': {'target': 'compiling', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'python_model_claim',
                    },
                }},
                'cfel_claim': {'target': 'processing_cfel', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'cfel_claim',
                    },
                }},
                'other_claim': {'target': 'ignoring', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'other_claim',
                    },
                }},
            }},
            'compiling': {'on': {
                'compiled': {'target': 'return_python', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'python_model_claim', 'outcome': 'compiled',
                    },
                }},
                'compilation_error': {'target': 'report_error', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C15.compilation_error', 'outcome': 'reported',
                    },
                }},
            }},
            'processing_cfel': {'on': {
                'comments_removed': {'target': 'return_cfel', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'cfel_comments', 'outcome': 'removed',
                    },
                }},
            }},
            'return_python': {'on': {
                'return_python': {'target': 'return_python_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C15.model_statements', 'outcome': 'python',
                    },
                }},
            }},
            'return_cfel': {'on': {
                'return_cfel': {'target': 'return_cfel_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C15.model_statements', 'outcome': 'comment_free_cfel',
                    },
                }},
            }},
            'ignoring': {'on': {
                'no_statements': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'no_statements',
                    },
                }},
            }},
            'done': {'type': 'final'},
            'failed': {'type': 'final'},
            'return_python_response': {'on': {
                'python_statements_returned': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'python_statements_returned',
                    },
                }},
            }},
            'return_cfel_response': {'on': {
                'cfel_statements_returned': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'cfel_statements_returned',
                    },
                }},
            }},
            'report_error': {'on': {
                'compilation_error': {'target': 'failed', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'compilation_error',
                    },
                }},
            }},
        },
    },
)
```
