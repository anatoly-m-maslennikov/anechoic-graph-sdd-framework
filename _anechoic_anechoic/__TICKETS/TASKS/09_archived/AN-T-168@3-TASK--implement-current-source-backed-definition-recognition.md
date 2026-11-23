---
atom_family: TKT
atom_id: AN-T-168
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 3
  updated_at: 2026-10-24 06:04:08 +0400
---
## Summary

Implement current source-backed definition recognition

# Summary

Implement current source-backed definition recognition

## Objective

Implement current source-backed definition recognition.

## Details

Assignee: AI Agent, as carried above. Estimated own work: 15 minutes.

Inputs: CA-P-1875; existing reader.

Required Plan prerequisites: [CA-P-1875](03-CA-P-1875-TASK--record-the-current-definition-extraction-contract.md).

Output: Implement current source-backed definition recognition with source-backed evidence retained in this Task's work record.

Acceptance check: Current-form positive fixtures; missing/ambiguous definitions remain honest limitations.

Exclusive edit/effect scope: 102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/GENERATE_ENTITY_GRAPH/ definition reader/extractor and its focused fixtures only.

Reuse current readers. Preserve source evidence, unique Active defining authority and matching governed target; do not rewrite source Atoms or create semantic authority to fit parser assumptions.

Inherit the main Epic's boundaries and the Operator's explicit 90% confidence threshold/retry rules. If the current work will exceed 15 minutes, split it into bounded admitted children before execution. Shared graph/fixture edits must be serialized or held by one integration owner. New required defects need separately bounded fix Tasks, not an unbounded review-and-fix loop.

### Definition of Done

the Plan is **not** Done **if** ((the source-backed output for "Implement current source-backed definition recognition" **or** required evidence is missing) **or** (the stated acceptance check is failed, blocked, stale, conflicting **or** incomplete) **or** (work exceeds the admitted boundary **or** required source/runtime admission is unavailable) **or** (a required effect **or** execution receipt remains uncertain **or** recording-pending) **or** (any direct decomposing Plan is **not** Done)).
