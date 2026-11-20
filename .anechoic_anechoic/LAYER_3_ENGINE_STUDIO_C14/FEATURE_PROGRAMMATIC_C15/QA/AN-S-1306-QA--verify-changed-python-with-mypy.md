---
identity:
  atom_id: AN-S-1306
context:
  container:
    component: C15
  tier: 6
  lens: QA
state:
  status: active
  version: 22
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify changed Python with Mypy

## Claim

### Prose Claim

New Python must pass strict admitted Mypy; changed Python must not regress below passing baseline. An incompatible return and unexplained broad suppression both reject the target; only a narrow explained accepted suppression can remain.
