---
atom_family: SPEC
atom_id: AN-S-4961
container:
  component: C86
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4960@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T21:35:58.956802+00:00'
---

## Summary

Validate the Lean translation.

## Claim

### Prose Claim

Normalize the claims and check emitted declarations and applicable executable
shapes. Report conflicts or unresolved expectations. Return `matched` only
when the checks pass and no finding is reported on that path.

On a bounded framing request, check both framing roles on the same finite
byte inputs. If the checks pass and no issue or unresolved translation
finding remains, return `bounded_match` with the witness inputs, results for
both roles, and unresolved coverage. On the default path, passing the
framing witnesses leaves framing equivalence `unresolved`.

### Formal Claim

```python
component_workflow(
    component='C86',
    action='validate_translation',
    machine={'id': 'c86_validate_translation',
 'initial': 'idle',
 'states': {'idle': {'on': {'requested': {'target': 'checking',
                                          'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}}}},
            'checking': {'on': {'matched_effect': {'target': 'return_matched',
                                                   'guard': {'type': 'matchesTrace',
                                                             'params': {'kind': 'effect',
                                                                        'target': 'C86.lean_declarations',
                                                                        'outcome': 'validated',
                                                                        'detail': {'model': 'request_normalized_model'}}}},
                                'bounded_match_effect': {'target': 'return_bounded_match',
                                                         'guard': {'type': 'matchesTrace',
                                                                   'params': {'kind': 'effect',
                                                                              'target': 'C86.framing_comparison',
                                                                              'outcome': 'reported'}}},
                                'conflicting_effect': {'target': 'return_conflicting',
                                                       'guard': {'type': 'matchesTrace',
                                                                 'params': {'kind': 'effect',
                                                                            'target': 'C86.translation_findings',
                                                                            'outcome': 'reported'}}},
                                'unresolved_effect': {'target': 'return_unresolved',
                                                      'guard': {'type': 'matchesTrace',
                                                                'params': {'kind': 'effect',
                                                                           'target': 'C86.translation_findings',
                                                                           'outcome': 'reported'}}}}},
            'done': {'type': 'final'},
            'return_matched': {'on': {'matched_returned': {'target': 'done',
                                                           'guard': {'type': 'matchesTrace',
                                                                     'params': {'kind': 'output',
                                                                                'outcome': 'matched'}}}}},
            'return_bounded_match': {'on': {'bounded_match_returned': {'target': 'done',
                                                                     'guard': {'type': 'matchesTrace',
                                                                               'params': {'kind': 'output',
                                                                                          'outcome': 'bounded_match'}}}}},
            'return_conflicting': {'on': {'conflicting_returned': {'target': 'done',
                                                                   'guard': {'type': 'matchesTrace',
                                                                             'params': {'kind': 'output',
                                                                                        'outcome': 'conflicting'}}}}},
            'return_unresolved': {'on': {'unresolved_returned': {'target': 'done',
                                                                 'guard': {'type': 'matchesTrace',
                                                                           'params': {'kind': 'output',
                                                                                      'outcome': 'unresolved'}}}}}}},
)
```
