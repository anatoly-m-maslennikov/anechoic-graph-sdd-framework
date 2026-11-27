---
atom_family: SPEC
atom_id: AN-S-5062
container:
  component: C35
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3076@5-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T11:22:36.001339+00:00'
---

## Summary

Reserve ATOM_ACTIONS.

## Claim

### Prose Claim

Keep Find, Check and Change distinct under AN-S-2397@5. Find reads the explicit frontier. Each mutation takes one explicit Atom. This Solution declares no direct Atom Action entry point.

### Formal Claim

```python group
component_group(
    roles={},
    entry_points=(),
)
```
