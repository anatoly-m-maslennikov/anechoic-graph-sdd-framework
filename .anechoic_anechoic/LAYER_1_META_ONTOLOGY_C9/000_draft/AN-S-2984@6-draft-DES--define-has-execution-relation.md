---
atom_family: SPEC
atom_id: AN-S-2984
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: draft
  version: 6
  updated_at: 2026-11-04 16:07:35 +0400
---
## Summary

Define HAS_EXECUTION Relation

## Claim

### Formal Claim

```python
# model
relation(source='Relation//HAS_EXECUTION', name='HAS_INVERSE', target='Relation//IS_EXECUTION_OF', reverse=True)
classify(address='Relation//HAS_EXECUTION', axis='Derivation', value='Derived', notation='relation')
# instances
relation(source='Workflow//$workflow', name='HAS_EXECUTION', target='Workflow Run//$workflow_run')
relation(source='Step//$step', name='HAS_EXECUTION', target='Step Run//$step_run')
relation(source='Action//$action', name='HAS_EXECUTION', target='Action Run//$action_run')
```

## Semantics

HAS_EXECUTION relates a reusable Workflow, Step or Action to its corresponding actual Run.
