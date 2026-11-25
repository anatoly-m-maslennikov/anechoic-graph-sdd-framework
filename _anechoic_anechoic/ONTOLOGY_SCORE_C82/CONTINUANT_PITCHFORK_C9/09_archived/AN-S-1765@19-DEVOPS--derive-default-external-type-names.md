---
atom_family: SPEC
atom_id: AN-S-1765
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 19
  updated_at: 2026-10-27 19:59:24 +0400
---
## Summary

Derive default external Type names

# Summary

Derive default external Type names

## Scope

external Type names derived from internal Types.

## Claim

**when** an external Type name is derived from an internal Type, the derivation uses `external_<internal_type_name>`. **when** the internal Type is the Content Role's default, the derived name uses that registered default Type. a separately registered explicit external Type name is non-default **and** does **not** modify this derivation rule.

## Details
