---
atom_family: SPEC
atom_id: AN-S-3626
container:
  component: C9
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Validate Specification **and** concrete content tiers

# Summary

Validate Specification **and** concrete content tiers

## Scope

classification of specification authority and concrete content tiers.

## Claim

the tier Evaluation **must** reject classification that confuses specification authority with the content it governs.

### Numeric tier fixtures

- classify an Atom from its complete Claim, owner Scope Unit, and the applicable definition; use numeric Tier `0` for an admitted Project Principle, Tier `1` for Core, Tier `2` for General, Tier `3` for Standard, and `-1` only for a Project-owned Goal.
- permit ordinary Project Atoms at Tier `0` or higher and non-Project Atoms at Tier `1` or higher; do not infer a tier from reuse, nesting, importance, filename labels, Content Role, or Type.
- preserve the source Atom's numeric Tier in a Projection or other derived carrier; the derived carrier does not acquire an independent Atom Tier.
- evaluate every stored governing RMED relation occurrence under CA-R-2149: a same-Scope target has a strictly lower Tier, while a strict-ancestor target is governed without comparing Tiers; descendant and sibling targets fail. Stored source-to-target direction is authoritative and derived inverses are excluded.
- unresolved owner, Scope ancestry, endpoint Tier, or registered relation membership remains unresolved and is not treated as a pass; no default Tier is applicable.
- no Content Role or Type restriction authorizes or forbids a numeric Tier; any role/type classification must still follow the complete Claim and the applicable definition.

## Details
