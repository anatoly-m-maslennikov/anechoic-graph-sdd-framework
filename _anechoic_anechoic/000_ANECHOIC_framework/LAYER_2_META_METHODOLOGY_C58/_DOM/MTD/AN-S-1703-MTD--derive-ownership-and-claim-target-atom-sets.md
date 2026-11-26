---
atom_family: SPEC
atom_id: AN-S-1703
container:
  component: C58
tier: 3
context:
  lens: DOM/MTD
state:
  status: "active"
  version: 43
  updated_at: "2026-11-25T22:20:07.819912+00:00"
---
## Summary

Derive Ownership **and** Claim-target Atom Sets

## Claim

### Prose Claim

This rule applies to legacy Scope Unit carriers. Use AN-S-3168 for the native Atom Container.


selection of Owned Atoms, Targeting Atoms, Subtree-owned Atoms, **and** Subtree-targeting Atoms for a Scope Unit.


**to** derive the four Atom sets for a selected Scope Unit, the resolver **must** perform **all** of:

1. establish the complete authoritative source frontier, including Atoms outside the selected subtree that can target a Scope Unit inside it; scanning **only** locally stored Atoms is insufficient for Targeting Atoms **or** Subtree-targeting Atoms.
2. read **every** candidate Atom's carried current Scope Unit **and** check it against its nearest containing Scope Unit, passing through Atom Collections **and** Plan Hub Carriers **without** treating their nesting as additional Scope Unit ownership. Apply the legacy Project Goal Operator-owner encoding under AN-S-1039@1 **when** no containing Scope Unit exists; do **not** invent a Scope Unit owner.
3. resolve **every** candidate's Claim Target Scope Unit independently of ownership. read the internally carried target; absence of a required value is invalid, **not** permission **to** infer it from placement; apply AN-S-1637@26 for the historical Subject-based Plan target. an unresolved required target remains unresolved. a reference **to** another Scope Unit **must not** transfer ownership, **and** the target **must** resolve **to** a Scope Unit, **not** a Hub Atom **or** another non-Scope-Unit object. Claim Scope restrictions remain **in** the body sections registered by CA-D-495, including Scope for RMED, **and** do **not** create extra targets.
4. derive Owned Atoms, Targeting Atoms, Subtree-owned Atoms, **and** Subtree-targeting Atoms under the historical rules AN-S-344@25, AN-S-345@25, AN-S-410@32, and AN-S-346@21 respectively. use the Scope Unit tree for descendant coverage; do **not** substitute physical subtree membership for Claim targeting **or** inferred inherited applicability for an explicit **or** default Claim target.
5. retain source Atom **and** Revision references **without** creating additional authoritative Atom copies. apply Content Role, Status, **and** other requested filters **after** resolving the selected set; the alias `spec` selects the Active RMED subset under AN-S-1706@22 for legacy Scope Unit selections, independently of numeric Tier.
6. report the exact missing source, owner, target, ancestry, **or** required filter value **and** withhold a complete affected result **when** it is unresolved **or** contradictory. a complete empty set remains empty; an incomplete frontier **must not** be reported as a complete empty set.
