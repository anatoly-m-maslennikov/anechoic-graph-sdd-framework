---
atom_family: TKT
atom_id: AN-T-2557
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 06:12:15 +0400
---
## Summary

Prepare independent current Subject review checks

# Summary

Prepare independent current Subject review checks

## Objective

Check review report coverage and evidence independently of each report producer.

## Details

Estimated own work: 15 minutes. This independent test-preparation lane is ready after CA-P-1972, despite the parent ledger's later all-review gate. Own only stage2/support/verify_current_subject_reviews.py, its isolated tests and task-2044 receipt. Keep the checker a small one-off ad-hoc script, not a reusable Tool or repair framework. Verify exact batch/source/occurrence rows and pins, actual owning current Main Content spans, finding dispositions, candidate pointer existence, confidence/decision consistency and non-executable boundaries. Deliberate corruption or omission must fail. Do not assert semantic sufficiency solely from hash/pointer existence; root's bounded meaning review remains required. This preparation does not integrate or accept any mappings.

Read and follow current-subjects.contract.md and current-subjects.review.contract.md. No Core, captured review, grammar, native admission, MCP/FPF, runtime or source mutation. Root owns integration and Git.

Completion: the read-only ad-hoc verifier checks exact pinned coverage, finding dispositions, owning content spans, candidate pointers, decision/confidence consistency and non-executable boundaries. Root independently reran all 14 isolated tests: PASS. Live report checks expose stale or incomplete evidence instead of accepting it. Structured read records and named or list evidence pins are supported. Semantic meaning acceptance remains separate. Evidence: stage2/task-2044.receipt.json.

### Definition of Done

Not Done if the assigned output or required checks are missing/stale, evidence or coverage failures are hidden, source writes occur, completion exceeds actual evidence, or own work exceeds 15 minutes without decomposition.
