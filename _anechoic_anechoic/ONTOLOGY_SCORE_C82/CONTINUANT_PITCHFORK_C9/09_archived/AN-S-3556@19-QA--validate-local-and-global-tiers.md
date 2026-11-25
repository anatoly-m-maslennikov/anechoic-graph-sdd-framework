---
atom_family: SPEC
atom_id: AN-S-3556
container:
  component: C9
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-22 16:17:20 +0000
---
## Summary

Validate Local **and** Global Tiers

# Summary

Validate Local **and** Global Tiers

## Scope

an Atom's Local Tier **and** Global Tier.

## Claim

the Evaluation **must** reject an Atom **if** **any** following condition holds:

- its Local Tier cardinality **or** admitted value violates CA-R-155-CORE_META_MODEL-CORE--give-every-non-project-goal-atom-one-local-tier, CA-R-680-CORE_META_MODEL-GENERAL-REQUIREMENT--order-project-local-tiers, CA-R-1442-CORE_META_MODEL-GENERAL-REQUIREMENT--order-non-project-local-tiers, the applicable Project Goal exception, **or** an applicable Goal, Type, **or** CAPO/I Standard restriction under CA-R-1566-CORE_META_MODEL-GENERAL-REQUIREMENT--keep-change-and-implementation-content-at-standard.
- its Global Tier violates the Project **or** recursive structural mapping.
- its Principle tier lies outside the Project under CA-R-1443-CORE_META_MODEL-CORE-REQUIREMENT--restrict-principle-to-project-scope.
- its non-Project Goal is **not** a Standard Atom of its direct parent Scope Unit.
- its ownership **or** structural ancestry is unresolved.
- its complete Claim fails the applicable Local Tier definition **and** the evidence procedure governed by CA-M-272-CORE_META_MODEL-METHOD--classify-an-atom-local-tier-from-its-complete-claim.
- its classification is unresolved **or** inferred from breadth, an old label, source ownership, importance, **or** reuse alone; applying the explicit CAPO/I Standard rule is required **and** is **not** unsupported role-based inference.
- a tier-parent edge is based on the value defined by an Atom rather than that Atom's own admitted tier.
- governance from Global Tier `N` **to** **any** greater Global Tier **in** the Scope Unit is omitted because of a different Content Role, a different Subject, a non-adjacent tier, **or** an unoccupied intermediate tier, contrary **to** CA-R-1573-CORE_META_MODEL-CORE-REQUIREMENT--govern-greater-global-tiers-within-each-scope-unit.

validate the internally carried Local Tier **and** Global Tier against the applicable mapping; a filename alone is **not** their source. filename interpretation follows CA-D-285-CORE_META_MODEL-DELIVERY--serialize-local-tier-filename-tokens: recognize the external Project Goal's tierless grammar **before** applying the ordinary omitted-Standard default. an incorrect tier inferred by ignoring that exception **must** fail this Evaluation.

## Details
