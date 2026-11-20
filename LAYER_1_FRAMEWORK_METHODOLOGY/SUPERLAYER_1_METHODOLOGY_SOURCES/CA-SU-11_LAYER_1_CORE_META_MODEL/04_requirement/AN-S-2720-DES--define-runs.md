---
atom_family: SPEC
atom_id: AN-S-2720
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 4
  updated_at: 2026-11-05 02:06:39 +0400
---
## Summary

Define RUNS

## Claim

### Prose Claim

RUNS binds a Step invocation to its Action or Workflow. Its inverse is IS_RUN_BY.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='RUNS',
    inverse_alias='IS_RUN_BY',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role:=Operations)/Step',)},
    target_endpoint={
        'level': 'instances',
        'entity_paths': ('Atom/(.Header.Context.Role:=Operations)/Action', 'Atom/(.Header.Context.Role:=Operations)/Workflow'),
    },
)
```

