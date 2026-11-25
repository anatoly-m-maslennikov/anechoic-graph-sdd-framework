---
atom_family: SPEC
atom_id: AN-S-3943
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Define Entity/Graph Rule.Default Value

# Summary

Define Entity/Graph Rule.Default Value

## Scope

The optional fallback value associated with a Graph Rule.

## Claim

Graph Rule.Default Value **means** an optional fallback used when the corresponding value is absent, without replacing an explicit value and subject to the applicable constraints.

## Details

The property is optional. Selecting a default does not automatically write or materialize that value. This definition supplies no concrete default, cross-rule precedence, merge behavior, or override policy.
