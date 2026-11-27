---
atom_family: SPEC
atom_id: AN-S-5029
container:
  component: C86
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-4933@1
state:
  status: "archived"
  version: 1
  updated_at: '2026-11-27T00:00:00Z'
---

## Summary

Validate the Lean translation.


## Claim

### Prose Claim

Normalize the claims. When claims are present, call C84 to evaluate the Lean
program before checking emitted declarations and applicable executable shapes.
A Lean evaluation or result-shape failure raises `ValueError`. Empty claims
return a conflict or unresolved diagnostic. Return `matched` only when the
checks pass and no finding is reported on that path.

On a bounded framing request, check both framing roles on the same finite
byte inputs. The result requires a nonempty witness set and observations
for both roles. If the checks pass and no issue or unresolved translation
finding remains, return `bounded_match` with the witness inputs, results for
both roles, and unresolved coverage. On the default path, passing the
framing witnesses leaves framing equivalence `unresolved`.


### Formal Claim

```python
component_workflow(
    component='C86', action='validate_translation',
    machine={'id': 'c86_validate_translation',
 'initial': 'idle',
 'states': {'idle': {'on': {'default_request': {'to': 'default_input',
                                                'expect': {'kind': 'trigger', 'detail': {'bounded_framing': False}}},
                            'bounded_request': {'to': 'bounded_input',
                                                'expect': {'kind': 'trigger', 'detail': {'bounded_framing': True}}}}},
            'default_input': {'on': {'empty_conflicting': {'to': 'return_conflicting',
                                                           'expect': {'kind': 'effect',
                                                                      'target': 'C86.translation_findings',
                                                                      'outcome': 'reported',
                                                                      'detail': {'claims': 'empty'}}},
                                     'empty_unresolved': {'to': 'return_unresolved',
                                                          'expect': {'kind': 'effect',
                                                                     'target': 'C86.translation_findings',
                                                                     'outcome': 'reported',
                                                                     'detail': {'claims': 'empty'}}},
                                     'claims_present': {'to': 'default_evaluate',
                                                        'expect': {'kind': 'effect',
                                                                   'target': 'C86.normalized_claims',
                                                                   'outcome': 'available',
                                                                   'detail': {'claims': 'nonempty'}}}}},
            'bounded_input': {'on': {'empty_conflicting': {'to': 'return_conflicting',
                                                           'expect': {'kind': 'effect',
                                                                      'target': 'C86.translation_findings',
                                                                      'outcome': 'reported',
                                                                      'detail': {'claims': 'empty'}}},
                                     'empty_unresolved': {'to': 'return_unresolved',
                                                          'expect': {'kind': 'effect',
                                                                     'target': 'C86.translation_findings',
                                                                     'outcome': 'reported',
                                                                     'detail': {'claims': 'empty'}}},
                                     'claims_present': {'to': 'bounded_evaluate',
                                                        'expect': {'kind': 'effect',
                                                                   'target': 'C86.normalized_claims',
                                                                   'outcome': 'available',
                                                                   'detail': {'claims': 'nonempty'}}}}},
            'default_checked': {'on': {'matched_effect': {'to': 'return_matched',
                                                          'expect': {'kind': 'effect',
                                                                     'target': 'C86.lean_declarations',
                                                                     'outcome': 'validated',
                                                                     'detail': {'model': 'request_normalized_model'}}},
                                       'conflicting_effect': {'to': 'return_conflicting',
                                                              'expect': {'kind': 'effect',
                                                                         'target': 'C86.translation_findings',
                                                                         'outcome': 'reported'}},
                                       'unresolved_effect': {'to': 'return_unresolved',
                                                             'expect': {'kind': 'effect',
                                                                        'target': 'C86.translation_findings',
                                                                        'outcome': 'reported'}},
                                       'invalid_shape': {'to': 'evaluation_failed',
                                                         'expect': {'kind': 'effect',
                                                                    'target': 'C86.evaluation_shape',
                                                                    'outcome': 'invalid'}}}},
            'bounded_checked': {'on': {'matched_effect': {'to': 'return_matched',
                                                          'expect': {'kind': 'effect',
                                                                     'target': 'C86.lean_declarations',
                                                                     'outcome': 'validated',
                                                                     'detail': {'model': 'request_normalized_model'}}},
                                       'conflicting_effect': {'to': 'return_conflicting',
                                                              'expect': {'kind': 'effect',
                                                                         'target': 'C86.translation_findings',
                                                                         'outcome': 'reported'}},
                                       'unresolved_effect': {'to': 'return_unresolved',
                                                             'expect': {'kind': 'effect',
                                                                        'target': 'C86.translation_findings',
                                                                        'outcome': 'reported'}},
                                       'bounded_match_effect': {'to': 'return_bounded_match',
                                                                'expect': {'kind': 'effect',
                                                                           'target': 'C86.framing_comparison',
                                                                           'outcome': 'reported'}},
                                       'invalid_shape': {'to': 'evaluation_failed',
                                                         'expect': {'kind': 'effect',
                                                                    'target': 'C86.evaluation_shape',
                                                                    'outcome': 'invalid'}}}},
            'return_matched': {'on': {'return': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'matched'}}}},
            'return_bounded_match': {'on': {'return': {'to': 'done',
                                                       'expect': {'kind': 'output', 'outcome': 'bounded_match'}}}},
            'return_conflicting': {'on': {'return': {'to': 'done',
                                                     'expect': {'kind': 'output', 'outcome': 'conflicting'}}}},
            'return_unresolved': {'on': {'return': {'to': 'done',
                                                    'expect': {'kind': 'output', 'outcome': 'unresolved'}}}},
            'evaluation_failed': {'on': {'raise': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}}}},
            'done': {'type': 'final'},
            'default_evaluate': {'on': {'lean_evaluated': {'to': 'default_checked',
                                                           'expect': {'kind': 'effect',
                                                                      'target': 'C84.lean_evaluation',
                                                                      'outcome': 'returned',
                                                                      'detail': {'component': 'C84',
                                                                                 'interface': 'run_lean_json',
                                                                                 'action': 'run_lean_json',
                                                                                 'output': 'fulfilled',
                                                                                 'manifest': 'AN-S-4931@1-draft'}}},
                                        'lean_failed': {'to': 'evaluation_failed',
                                                        'expect': {'kind': 'effect',
                                                                   'target': 'C84.lean_evaluation',
                                                                   'outcome': 'failed',
                                                                   'detail': {'component': 'C84',
                                                                              'interface': 'run_lean_json',
                                                                              'action': 'run_lean_json',
                                                                              'output': 'failed',
                                                                              'manifest': 'AN-S-4931@1-draft'}}}}},
            'bounded_evaluate': {'on': {'lean_evaluated': {'to': 'bounded_checked',
                                                           'expect': {'kind': 'effect',
                                                                      'target': 'C84.lean_evaluation',
                                                                      'outcome': 'returned',
                                                                      'detail': {'component': 'C84',
                                                                                 'interface': 'run_lean_json',
                                                                                 'action': 'run_lean_json',
                                                                                 'output': 'fulfilled',
                                                                                 'manifest': 'AN-S-4931@1-draft'}}},
                                        'lean_failed': {'to': 'evaluation_failed',
                                                        'expect': {'kind': 'effect',
                                                                   'target': 'C84.lean_evaluation',
                                                                   'outcome': 'failed',
                                                                   'detail': {'component': 'C84',
                                                                              'interface': 'run_lean_json',
                                                                              'action': 'run_lean_json',
                                                                              'output': 'failed',
                                                                              'manifest': 'AN-S-4931@1-draft'}}}}}}},
)
```
