---
atom_family: TKT
atom_id: AN-T-2589
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-10-11 14:39:13 +0400
---
## Summary

Record approved quarantine decisions

# Summary

Record approved quarantine decisions

## Objective

The actual Operator choices for legacy Atom IDs and timestamp serialization are recorded without inventing selector approval.

## Details

Own work: at most fifteen minutes. Record the actual reply and exact audited input pins; update the current Epic checkpoint. Keep captured reports and original Core unchanged.

## Completion

Recorded the Operator's choice to migrate the six legacy IDs to new canonical IDs and to use quoted timestamps with explicit UTC offsets. The selector question remains open because the Operator requested an explanation. Evidence: `_projection/core-entity-review/stage2/operator.quarantine-decisions.2026-10-11.json`. This Task records decisions only; no successor ID was allocated, timestamp policy adopted, original source changed, or source migration performed.

### Definition of Done

Not Done if the recorded choices differ from the actual reply, selector approval is inferred, current input pins are stale, historical evidence or source contents change, or a decision record is presented as an execution receipt.
