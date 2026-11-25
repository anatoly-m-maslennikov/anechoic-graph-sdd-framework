---
atom_family: SPEC
atom_id: AN-S-4991
container:
  component: C38
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4990@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T00:00:00+00:00'
---

## Summary

Append a journal entry.

## Claim

### Prose Claim

Append one supplied entry to a Journal. C30 owns Journal I/O. Find and Fetch remain outside this narrow claim.

The successful Append reports the entry as appended. The input shape, selection rules, failure behavior and underlying I/O effects remain open.

### Formal Claim

```python
component_workflow(
    component='C38', action='append_journal_entry',
    machine={
        'id': 'c38_append_journal_entry', 'initial': 'idle',
        'states': {
            'idle': {'on': {'request': {'target': 'working', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}}}},
            'working': {'on': {'effect_0': {'target': 'returning', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'journal_entry', 'outcome': 'appended'}}}}},
            'returning': {'on': {'return': {'target': 'returned', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'entry_appended'}}}}},
            'returned': {'type': 'final'},
        },
    },
)
```

## Details

The trace models only the named successful outcome. It does not prove the input, failure rules, or unmodeled effects.
