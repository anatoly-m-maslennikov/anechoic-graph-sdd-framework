---
atom_family: SPEC
atom_id: AN-S-2752
container:
  component: C58
tier: 2
context:
  lens: DOM/MTD
state:
  status: "archived"
  version: 40
  updated_at: "2026-11-26T09:59:58.537853+00:00"
---

## Summary

Author Plan Atoms

## Claim

### Prose Claim

For a native Work Report, use the `work_report` Ticket Asset Template and give the report a Summary of its own contribution. For a report attached to a Task, use the Task as its declared Container. Place an unbound report under Ticket Assets as specified by AN-S-3160. Record actual changes, checks performed, results, and remaining gaps. Update the record as work proceeds.

For a legacy Plan / Work Report, apply AN-S-2598. For other legacy Plan Forms, apply the common Plan rules independently of Label:

1. State the intended work or outcome and provide own work, direct Plan decomposition, or both under the historical AN-S-1632@27. Use AN-S-1638@24 when validating the historical executable leaf-work rule.
2. Resolve the active Subject and its target Scope under CA-R-1588. Apply the applicable completion and verification rules, including the historical AN-S-1643@24, and use Labels only under their governing rules. For a containing Plan whose Status is Done or Canceled, require every directly contained Plan to be Done or Canceled; mixed terminal statuses are allowed, and containment does not force a child Status to match the parent.
3. Express required start dependencies as direct `IS_BLOCKED_BY` Relations on the dependent Plan and derive `BLOCKS`. For Plan containment, declare `IS_CONTAINED_BY` on the child and derive `CONTAINS`. Do not infer dependencies from numbers or folder placement.
4. Resolve confidence from its applicable sources and store only an explicitly selected confidence override under its admitted encoding.
5. Review the finalized intended contribution against its supporting content and completion criteria, then write the Summary under AN-S-2574. Apply AN-S-1604 to determine whether a change starts a new identity.
