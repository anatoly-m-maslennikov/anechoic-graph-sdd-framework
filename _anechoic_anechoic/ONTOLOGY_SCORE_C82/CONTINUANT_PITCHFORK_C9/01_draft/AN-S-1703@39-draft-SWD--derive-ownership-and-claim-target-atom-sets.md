---
atom_family: SPEC
atom_id: AN-S-1703
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: "draft"
  version: 39
  updated_at: "2026-11-25T21:17:25.284026+00:00"
---
## Summary

Derive Ownership **and** Claim-target Atom Sets

## Claim

### Prose Claim


selection of Owned Atoms, Targeting Atoms, Subtree-owned Atoms, **and** Subtree-targeting Atoms for a Scope Unit.


**to** derive the four Atom sets for a selected Scope Unit, the resolver **must** perform **all** of:

1. establish the complete authoritative source frontier, including Atoms outside the selected subtree that can target a Scope Unit inside it; scanning **only** locally stored Atoms is insufficient for Targeting Atoms **or** Subtree-targeting Atoms.
2. resolve **every** candidate Atom's containing Scope Unit from its `Header.Container` chain: follow Atom container references until reaching a Scope Unit ID. The predefined Scope Unit `world` (`CA-SU--1`) is valid. Do **not** infer ownership from directory nesting **or** invent a Scope Unit owner.
3. resolve **every** candidate's Claim Target Scope Unit independently of ownership. read the internally carried target; absence of a required value is invalid, **not** permission **to** infer it from placement; apply CA-R-1588-CORE_META_MODEL-RULE--default-plan-target-to-the-enclosing-scope-unit for Plans within Plan containment. an unresolved required target remains unresolved. a reference **to** another Scope Unit **must not** transfer ownership, **and** the target **must** resolve **to** a Scope Unit, **not** a Hub Atom **or** another non-Scope-Unit object. Claim Scope restrictions remain **in** the body sections registered by CA-D-495, including Scope for RMED, **and** do **not** create extra targets.
4. derive Owned Atoms, Targeting Atoms, Subtree-owned Atoms, **and** Subtree-targeting Atoms under CA-R-1447-CORE_META_MODEL-GENERAL-REQUIREMENT--define-owned-atoms, CA-R-1448-CORE_META_MODEL-GENERAL-REQUIREMENT--define-targeting-atoms, CA-R-942-CORE_META_MODEL-DEFINITION--define-subtree-owned-atoms, **and** CA-R-1449-CORE_META_MODEL-GENERAL-REQUIREMENT--define-subtree-targeting-atoms respectively. use the Scope Unit tree for descendant coverage; do **not** substitute physical subtree membership for Claim targeting **or** inferred inherited applicability for an explicit **or** default Claim target.
5. retain source Atom **and** Revision references **without** creating additional authoritative Atom copies. apply Content Role, Status, **and** other requested filters **after** resolving the selected set; the alias `spec` selects the Active RMED subset under AN-S-1706@22 for legacy Scope Unit selections, independently of numeric Tier.
6. report the exact missing source, owner, target, ancestry, **or** required filter value **and** withhold a complete affected result **when** it is unresolved **or** contradictory. a complete empty set remains empty; an incomplete frontier **must not** be reported as a complete empty set.
