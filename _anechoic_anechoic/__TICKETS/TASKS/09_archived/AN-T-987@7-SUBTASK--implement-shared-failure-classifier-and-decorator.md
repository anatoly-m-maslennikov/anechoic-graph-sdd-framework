---
atom_family: TKT
atom_id: AN-T-987
container:
  component: C15
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 10:35:14 +0400
---
## Summary

Implement shared failure classifier and decorator

# Summary

Implement shared failure classifier and decorator

## Objective

Build one transport-neutral sync/async boundary with explicit failure classification, caller-owned response adapters, and existing diagnostic logging. Python RuntimeError alone must not mean blocking runtime failure. Preserve cancellation, metadata and caller result/effect ownership.

## Details

One Task per file. After completion, review and update dependant Tasks before their execution. Actual business Workflow lifecycle recording remains with its declared executor; this Task does not invent it in an error decorator.

### Definition of Done

Focused semantic/function tests cover ordinary success, request failures, explicit blocking runtime failures, logging failure and cancellation. At most 15 minutes own work; split further if required.

### Execution checkpoint

The independent review follow-up is complete: actual exception classes are retained only when an exception exists; synthetic refusals do not invent one. Diagnostic severity is constrained to ERROR/WARNING/INFO/DEBUG. Ten focused boundary cases pass, including cancellation and diagnostic-sink failures, and scoped Ruff passes. The final related 32-case rerun also passes. Shared API and old positional FailureRecord construction are preserved; no retry or Journal side effects. Final independent review: APPROVED. Source/focused-test acceptance only, not deployment.
