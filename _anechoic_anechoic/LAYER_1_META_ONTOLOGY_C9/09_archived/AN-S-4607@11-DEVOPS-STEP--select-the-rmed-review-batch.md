---
atom_family: SPEC
atom_id: AN-S-4607
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 11
  updated_at: 2026-10-19 15:56:53 +0400
---
## Summary

Select the RMED review batch

# Summary

Select the RMED review batch

## Operation

RMED Review Selection Step **means** the Workflow node invoking **`=1`** Action, CA-O-105, **in** Integrated context.

- bind the active RMED request, carried source inventory, selection data, compact `atom_local` rule pack, **and** temporary output directory.
- carry the caller's Workflow name, Run ID, full report location, **and** shared Journal reference with the selected queue, including an empty **or** blocked result.
- record the original selected queue, source observations, **and** pending work **in** **`=1`** progress list.
- pass the full selection **and** shared rules **to** the caller for dispatch **in** the check phase; native file **and** session capabilities are sufficient.

## Details

the Step selects work **without** modifying source Atoms. it does **not** load global Entity **or** relation graphs for evaluation.
