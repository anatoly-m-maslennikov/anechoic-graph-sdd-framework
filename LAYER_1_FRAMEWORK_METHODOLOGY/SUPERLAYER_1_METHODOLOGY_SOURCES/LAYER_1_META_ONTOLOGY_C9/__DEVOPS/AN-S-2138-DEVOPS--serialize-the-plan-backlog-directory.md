---
atom_family: SPEC
atom_id: AN-S-2138
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 29
  updated_at: '2026-11-12T19:34:44.489998+00:00'
---
## Summary

Serialize the Plan Backlog directory

## Claim

### Prose Claim

The Plan Backlog directory is `<owning scope unit>/<Plan Role folder>/<status folder>/`. It is a shared placement folder.

- Place a Backlog Plan directly in that folder when its direct Container is a Scope Unit or a Plan outside the Backlog group.
- When the direct Container is a Backlog Plan, place the file in that Plan's matching directory. Apply the same rule recursively.
- A Backlog Plan with contained Plans retains its matching directory and applicable descendant layout. Version labels use the ordinary Plan filename rule.
- Preserve the logical Container when placement uses the shared folder. Resolve containment from the Atom's Container.

The Formal Claim supplies the shared base directory. The direct Backlog Container rule supplies the more specific containing directory.

### Formal Claim

```python
placement_rules = ({"kind": "status", "role": "plan", "status": "backlog", "base": "role", "folder": "<status folder>"},)
```
