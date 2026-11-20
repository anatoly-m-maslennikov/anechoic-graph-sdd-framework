---
identity:
  atom_id: AN-S-1765
context:
  container:
    component: C9
  tier: 3
  lens: DevOps
state:
  status: active
  version: 23
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Derive default external Type names

## Claim

### Prose Claim


external Type names derived from internal Types.


**when** an external Type name is derived from an internal Type, the derivation uses `external_<internal_type_name>`. **when** the internal Type is the Content Role's default, the derived name uses that registered default Type. a separately registered explicit external Type name is non-default **and** does **not** modify this derivation rule.
