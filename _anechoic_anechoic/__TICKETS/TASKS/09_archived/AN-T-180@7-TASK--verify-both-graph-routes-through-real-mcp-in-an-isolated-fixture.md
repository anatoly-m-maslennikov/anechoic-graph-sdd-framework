---
atom_family: TKT
atom_id: AN-T-180
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 10:08:20 +0400
---
## Summary

Verify both graph routes through real MCP in an isolated fixture

# Summary

Verify both graph routes through real MCP in an isolated fixture

## Objective

Verify both graph routes through real MCP in an isolated fixture.

## Details

Assignee: AI Agent, as carried above. Estimated own work: 15 minutes.

Inputs: CA-P-1874, CA-P-1884, CA-P-1885; explicitly initialized test runtime.

Required Plan prerequisites: [CA-P-1874](02-CA-P-1874-TASK--expose-selected-route-admission-failures-in-discovery.md), [CA-P-1884](10-CA-P-1884-TASK--add-current-form-golden-graph-fidelity-cases.md), [CA-P-1885](11-CA-P-1885-EPIC--complete-graph-determinism-failure-and-recovery-verification.md).

Output: Verify both graph routes through real MCP in an isolated fixture with source-backed evidence retained in this Task's work record.

Acceptance check: Tested implementation fingerprint, exact schemas, actual graph effects and required durable receipts; no claim of live Core proof.

Exclusive edit/effect scope: Explicitly admitted isolated fixture runtime and both existing graph routes; retain fixture outputs/receipts. Do not activate the live Project runtime or claim live Core proof.

Identify the exact tested implementation generation/fingerprint and its source binding; retain exact schemas, actual effects and durable required receipts. Fixture proof is distinct from live Core proof. No implicit runtime start or global dependency installation.

Inherit the main Epic's boundaries and the Operator's explicit 90% confidence threshold/retry rules. If the current work will exceed 15 minutes, split it into bounded admitted children before execution. Shared graph/fixture edits must be serialized or held by one integration owner. New required defects need separately bounded fix Tasks, not an unbounded review-and-fix loop.

### Definition of Done

the Plan is **not** Done **if** ((the source-backed output for "Verify both graph routes through real MCP in an isolated fixture" **or** required evidence is missing) **or** (the stated acceptance check is failed, blocked, stale, conflicting **or** incomplete) **or** (work exceeds the admitted boundary **or** required source/runtime admission is unavailable) **or** (a required effect **or** execution receipt remains uncertain **or** recording-pending) **or** (any direct decomposing Plan is **not** Done)).
