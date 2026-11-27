---
atom_family: SPEC
atom_id: AN-S-5042
container:
  component: C16
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3056@68-draft
state:
  status: draft
  version: 1
  updated_at: "2026-11-27T00:01:49.527660+00:00"
---

## Summary

Update one exact authored Draft

## Claim

### Prose Claim

Validate the exact selector and requested changes. Under the Project write
lock, revalidate the captured Draft and optional timestamp. Replace only
that carrier with a digest precondition, then confirm the written bytes.
Return its identity and timestamp when confirmation succeeds.
Report a refused replacement with no write receipt. If the replacement
occurred and confirmation failed, return its unknown receipt and
`effect_uncertain` error without an artifact.

### Formal Claim

```python
component_workflow(component='C16', action='update_exact_draft', machine={
    'id': 'update_exact_draft', 'initial': 'idle', 'states': {
        'idle': {'on': {'request': {'expect': {'kind': 'trigger'}, 'to': 'validate'}}},
        'validate': {'on': {
            'invalid': {'expect': {'kind': 'output', 'outcome': 'preflight_rejected'}, 'to': 'done'},
            'valid': {'expect': {'kind': 'effect', 'target': 'C16.draft', 'outcome': 'validated'}, 'to': 'revalidate'}}},
        'revalidate': {'on': {
            'stale': {'expect': {'kind': 'output', 'outcome': 'preflight_rejected'}, 'to': 'done'},
            'current': {'expect': {'kind': 'effect', 'target': 'C16.draft', 'outcome': 'revalidated'}, 'to': 'replace'}}},
        'replace': {'on': {
            'refused': {'expect': {'kind': 'output', 'outcome': 'write_rejected'}, 'to': 'done'},
            'written': {'expect': {'kind': 'effect', 'target': 'C16.draft_write', 'outcome': 'replaced'}, 'to': 'confirm'}}},
        'confirm': {'on': {
            'confirmed': {'expect': {'kind': 'effect', 'target': 'C16.draft', 'outcome': 'confirmed'}, 'to': 'result'},
            'unconfirmed': {'expect': {'kind': 'effect', 'target': 'C16.draft', 'outcome': 'confirmation_uncertain',
                                       'detail': {'code': 'effect_uncertain'}}, 'to': 'uncertain'}}},
        'result': {'on': {'completed': {'expect': {'kind': 'output', 'outcome': 'completed'}, 'to': 'done'}}},
        'uncertain': {'on': {'reported': {'expect': {'kind': 'output', 'outcome': 'effect_uncertain'}, 'to': 'done'}}},
        'done': {'type': 'final'},
    }})
```

## Details

Compare the declared paths in Lean and exercise the file outcomes
through the exact Draft CLI.
