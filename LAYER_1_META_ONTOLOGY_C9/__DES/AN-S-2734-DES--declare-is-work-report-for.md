---
atom_family: SPEC
atom_id: AN-S-2734
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---

## Summary

Declare IS_WORK_REPORT_FOR

## Claim

### Prose Claim

The Host is a Plan / Work Report. The Target is the reported work Plan with Form Plan.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_WORK_REPORT_FOR',
    source_endpoint={'level': 'instances',
 'entity_paths': ('Atom/(.Header.Context.Role := Plan)/(.Header.Context.Form := Work '
                  'Report)',)},
    target_endpoint={'level': 'instances',
 'entity_paths': ('Atom/(.Header.Context.Role := Plan)/(.Header.Context.Form := '
                  'Plan)',)},
)
```

## Semantics

IS_WORK_REPORT_FOR relates a Work Report to its Task.
