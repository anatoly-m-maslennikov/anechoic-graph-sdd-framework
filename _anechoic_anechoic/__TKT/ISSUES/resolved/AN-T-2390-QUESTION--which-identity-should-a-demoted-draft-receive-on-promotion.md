---
atom_family: TKT
atom_id: AN-T-2390
structure:
  container:
    component: C00
  priority: 2
context:
  template: question
state:
  status: resolved
  version: 4
  updated_at: 2026-10-23 03:14:50 +0400
---
# Summary

Which identity should a demoted Draft receive on promotion?

## Concern

For an identified Atom changed to ID-free Draft and later promoted, should an available genuine identified predecessor restore the old Atom ID as optional evidence, or should every promotion allocate a fresh ID? Manually authored Drafts without prior identity get a fresh unused ID either way.

## Evidences

The Operator explicitly removed mandatory Draft history/Journal gates. D568/D570 now prohibit retained-head/origin/lineage/consuming-successor admission. D446 preserves same-Atom demotion without carrying its assigned ID. Prior implementation restored a demoted ID only by mandatory trusted history. Restoring known same-Atom identity and not guessing from missing records must be reconciled explicitly. The Operator answered: "keep it simple, so #2. keep it simple everywhere. no special cases". Every ID-free Draft promotion allocates a fresh unused ID, including tool-demoted Drafts; no optional-history identity restoration remains. D446/D568/D570 and the native implementation are being aligned to this explicit decision.

## Blast radius

The identity choice is resolved; implementation and independent checks remain separate work. Manual Draft promotion, admitted Status support, independent Journal recording and ordinary safeguards proceed independently.
