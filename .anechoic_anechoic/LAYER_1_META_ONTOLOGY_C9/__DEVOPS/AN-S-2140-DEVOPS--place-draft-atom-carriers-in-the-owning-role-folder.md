---
atom_family: SPEC
atom_id: AN-S-2140
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 5
  updated_at: '2026-11-12T19:34:49.576334+00:00'
---
## Summary

Place Draft Atom Carriers in the owning Role folder

## Claim

### Prose Claim

Place Draft Atom Markdown Carriers in the shared `<owning scope unit>/<role folder>/<status folder>/` directory. The Atom's owning Scope Unit and Role determine this directory.

### Formal Claim

```python
placement_rules = ({"kind": "status", "role": None, "status": "draft", "base": "role", "folder": "<status folder>"},)
```
