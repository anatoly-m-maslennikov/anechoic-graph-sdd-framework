---
atom_family: SPEC
atom_id: AN-S-3969
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-10-23 23:33:48 +0400
---
## Summary

Classify an Atom Numeric Tier from its Complete Claim

# Summary

Classify an Atom Numeric Tier from its Complete Claim

## Scope

classification of an Atom's numeric Tier against the range admitted by its owning Scope Unit.

## Claim

**to** classify one Atom's numeric Tier, the Author **must** perform **all** of:

1. resolve the exact Current Atom identity and Revision, complete independently replaceable Claim, governed Subject, owner, Atom Scope, Claim Target Scope Unit, textual Claim Scope, Content Role, Type, and governing boundary. Resolve the owning Scope Unit and apply CA-R-2130 for ordinary Project Atoms, CA-R-2131 for ordinary non-Project Atoms, and CA-R-2132 for Project Goal Atoms. A missing owner, Scope, target, or boundary remains unresolved; it is not filled from a filename, role, Type, source ownership, or breadth.
2. test the complete Claim against the initial numeric-tier definitions: Tier `0` Principle under CA-R-2126, Tier `1` Core under CA-R-2127, Tier `2` General under CA-R-2128, and Tier `3` Standard under CA-R-2129. These display names describe the initial named coordinates; they do not impose a Content-Role or Type-to-Tier restriction, and higher integer Tiers remain admissible where the owning Scope Unit admits them.
3. preserve the exact source identity, Revision, Claim contribution, evidence for the selected integer, owner and target Scope Units, and direct Relation effects before accepting the classification. A derived display token or filename omission is not the Tier source. Do not infer a Tier from reuse, importance, nesting, Content Role, Type, or a retired local/global label.
4. when checking a governing RMED Relation, apply CA-R-2149: in the same Scope Unit the stored target Tier must be strictly lower than the source Tier; for a strict ancestor Scope Unit, do not compare Tiers; descendant and sibling targets are forbidden. Derived inverse views are not governing occurrences.
5. return an identified unresolved result when the range, Claim evidence, ownership, Scope ancestry, endpoint state, or direct Relation direction is unresolved or conflicting. Preserve identity and unchanged Claim meaning; request one exact Operator disposition only when a material unresolved proposition remains below the effective Autonomous Confidence Threshold.

## Details

