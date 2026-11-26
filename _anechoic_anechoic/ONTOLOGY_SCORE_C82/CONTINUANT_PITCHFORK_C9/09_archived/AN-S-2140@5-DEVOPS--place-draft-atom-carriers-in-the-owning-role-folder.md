---
atom_family: SPEC
atom_id: AN-S-2140
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-25T21:23:34.793752+00:00"
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
