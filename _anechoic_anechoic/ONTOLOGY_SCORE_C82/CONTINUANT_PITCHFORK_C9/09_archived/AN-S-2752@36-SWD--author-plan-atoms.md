---
atom_family: SPEC
atom_id: AN-S-2752
container:
  component: C9
tier: 2
context:
  lens: SWD
state:
  status: "archived"
  version: 36
  updated_at: "2026-11-25T20:32:21.370721+00:00"
---

## Summary

Author Plan Atoms

## Claim

### Prose Claim

To author a Work Report, bind its Task through IS_WORK_REPORT_FOR, copy that Task’s Summary and Container, and record actual changes, checks, results and remaining gaps in Details. Update the record throughout execution.

For other Plan Forms, apply the common Plan rules independently of Label:

1. State the intended work or outcome and provide own work, direct Plan decomposition, or both under CA-R-1575. Apply the executable leaf-work bound under CA-R-1589.
2. Resolve the active Subject and its target Scope under CA-R-1588. Apply the applicable completion and verification rules, including CA-R-1599, and use Labels only under their governing rules. For a containing Plan whose Status is Done or Canceled, require every directly contained Plan to be Done or Canceled; mixed terminal statuses are allowed, and containment does not force a child Status to match the parent.
3. Express required start dependencies as direct `IS_BLOCKED_BY` Relations on the dependent Plan and derive `BLOCKS`. For Plan containment, declare `IS_CONTAINED_BY` on the child and derive `CONTAINS`. Do not infer dependencies from numbers or folder placement.
4. Resolve confidence from its applicable sources and store only an explicitly selected confidence override under its admitted encoding.
5. Review the finalized intended contribution against its supporting content and completion criteria, then derive Summary under CA-R-1418 and CA-R-2499. Preserve Summary across Revisions; a changed Summary requires the applicable replacement identity under CA-R-1464.
