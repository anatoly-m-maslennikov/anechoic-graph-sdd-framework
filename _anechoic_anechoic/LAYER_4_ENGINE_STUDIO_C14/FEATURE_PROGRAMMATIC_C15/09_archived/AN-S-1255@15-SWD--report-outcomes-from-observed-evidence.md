---
atom_family: SPEC
atom_id: AN-S-1255
container:
  component: C15
tier: 1
context:
  lens: SWD
state:
  status: archived
  version: 15
  updated_at: "2026-11-27T16:29:34.309627+00:00"
---

## Summary

Report outcomes from observed evidence

## Claim

### Prose Claim

**To** execute PROGRAMMATIC behavior and report its outcome, compare the requested result with observed effects and retained execution evidence, distinguish verified completion, verified no-op, partial effects and uncertain effects, and reuse established evidence rather than blindly replaying completed or uncertain mutations.

Resume is allowed only where the existing lifecycle or operation contract already admits it. Before a dependent step, preserve successful partial steps; on resume, read the actual observed state and continue from it without overwriting or replaying completed work. This policy does not require new receipts, retry or recovery machinery for every operation.

## Details

### Scope

New or changed PROGRAMMATIC implementation, including Tools, Apps, MCP adapters and tests.


- A returned call, scheduler completion or absence of reported errors does not alone establish the requested result.
- A no-op means the requested state was already satisfied and remained unchanged; do not fabricate writes or history.
- Preserve partial results, uncertainty, gaps and blockers honestly. Outcome reporting introduces no automatic retry or recovery policy. Do not infer that a resume is admitted from ordinary error text; use the existing lifecycle state and contract. When resume is admitted, retain successful partial work and do not replay completed steps.


### Retained partial-result presentation

When an operation has completed only part of the request, retain and present the verified completed results first, followed by the attributable errors and unfinished or uncertain work, without representing aggregate success.

#### Details

##### Scope

Use the scope for changed PROGRAMMATIC implementation in AN-S-1252.

1. At the operation owner, retain actual completed items and observed effects as work proceeds. A general exception wrapper cannot reconstruct lost local progress or decide business commit boundaries.
2. Return completed data together with errors in the same applicable response contract. Mark incompleteness or partial outcome explicitly and identify failed, skipped, unattempted and uncertain items where known. Do not discard useful verified data because another independent item failed.
3. Results-before-errors is presentation and consumption priority, not a demand for JSON member ordering or a new universal response schema. Preserve each transport's governed result contract while making both available.
4. Do not label an unverified, rolled-back or uncertain effect as completed, leak unsafe/private intermediate data, broaden an effect frontier, or weaken an explicitly atomic operation. If no verified result exists, state that honestly.
5. Do not introduce automatic retry, compensation or replay. Preserve actual recovery information and leave those actions with their declared owner.
