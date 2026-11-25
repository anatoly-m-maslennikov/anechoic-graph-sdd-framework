---
atom_family: SPEC
atom_id: AN-S-2137
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 28
  updated_at: "2026-11-25T23:12:31.473231+00:00"
---
## Summary

Place Carriers by Applicable Status Delivery

## Claim

### Prose Claim

Resolve the Current Atom's base directory from its logical Container.

- Scope Unit Container. Use the Atom's Role folder in that Scope Unit.
- Atom Container. Use the containing Atom's matching directory.

Place Active Atoms directly in the base directory. Place other Current Atoms in the derived Status folder within that base.

For other Artifacts, use the most specific applicable Delivery rule. Where a qualified Artifact Status model exists and no specific mapping applies, Active uses the canonical Current directory and another Status uses its lowercase Status subfolder. Where there is no qualified Status model, derive placement from the Artifact's Delivery rule.

### Formal Claim

```python
placement_rules = (
    {"kind": "status", "role": None, "status": "*", "base": "container", "folder": "<status folder>"},
    {"kind": "status", "role": None, "status": "active", "base": "container", "folder": ""},
)
```
