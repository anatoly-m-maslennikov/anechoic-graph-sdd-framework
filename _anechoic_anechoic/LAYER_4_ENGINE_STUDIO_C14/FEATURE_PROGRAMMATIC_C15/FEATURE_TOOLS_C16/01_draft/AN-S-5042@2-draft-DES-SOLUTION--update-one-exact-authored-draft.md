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
  - AN-S-3056@69-draft
state:
  status: draft
  version: 2
  updated_at: '2026-11-27T10:55:20+00:00'
---

## Summary

Update one exact authored Draft

## Claim

### Prose Claim

Validate the exact selector and requested changes. Under the Project write
lock, revalidate the captured Draft and optional timestamp. If the body
and authored Relations are unchanged, return the existing artifact with
its Version and Updated At. Preserve the exact Carrier bytes and return
no modify receipt.

For a change, replace only that Carrier with a digest precondition, then
confirm the written bytes. Return its identity and timestamp when
confirmation succeeds.
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
            'current': {'expect': {'kind': 'effect', 'target': 'C16.draft', 'outcome': 'revalidated'}, 'to': 'apply'}}},
        'apply': {'on': {
            'unchanged': {'expect': {'kind': 'effect', 'target': 'C16.draft', 'outcome': 'verified_unchanged'}, 'to': 'unchanged'},
            'refused': {'expect': {'kind': 'output', 'outcome': 'write_rejected'}, 'to': 'done'},
            'written': {'expect': {'kind': 'effect', 'target': 'C16.draft_write', 'outcome': 'replaced'}, 'to': 'confirm'}}},
        'confirm': {'on': {
            'confirmed': {'expect': {'kind': 'effect', 'target': 'C16.draft', 'outcome': 'confirmed'}, 'to': 'result'},
            'unconfirmed': {'expect': {'kind': 'effect', 'target': 'C16.draft', 'outcome': 'confirmation_uncertain',
                                       'detail': {'code': 'effect_uncertain'}}, 'to': 'uncertain'}}},
        'result': {'on': {'completed': {'expect': {'kind': 'output', 'outcome': 'completed'}, 'to': 'done'}}},
        'unchanged': {'on': {'no_change': {'expect': {'kind': 'output', 'outcome': 'no_change'}, 'to': 'done'}}},
        'uncertain': {'on': {'reported': {'expect': {'kind': 'output', 'outcome': 'effect_uncertain'}, 'to': 'done'}}},
        'done': {'type': 'final'},
    }})
```

## Details

The Action covers the exact Draft form of `atom_lifecycle_update` in
`native_lifecycle_cli`. It admits `S`, `T`, `P`, and `C` references under
the bound Project prefix. The governed effect is the Draft Carrier
replacement. The Project write lock may also be taken on refusal.

The trace outcome labels describe the comparison cases. The CLI returns
`completed` for the `no_change` case, with the existing artifact and an
empty effects list. Other CLI replies use their native outcome and error
fields.
