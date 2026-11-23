---
atom_family: TKT
atom_id: AN-T-1547
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 8
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Provide fixed isolated suite scratch

# Summary

Provide fixed isolated suite scratch

## Objective

Provide fixed isolated suite scratch under the parent's exact source contract.

## Details

suite_scratch_executor exclusively owns RELEASE_VERSION/release_suite_execution.py and tests/test_release_suite_execution.py.

Estimated execution slice <=15 minutes. Preserve other workers' changes. Root alone owns index, commits and actual shared runtime effects. Tests and disposable smoke evidence are not release promotion.

## Definition of Done

Fixed bounded tmpfs regression and actual disposable Docker scratch smoke pass; source bind stays read-only.

## Pre-execution review

Root accepts this exclusive bounded assignment as the minimal current parent repair. Preserve installed N and truthful observed effects.

## Recorded verification

8b8d74bb5; eleven executor tests and actual disposable Docker scratch smoke passed with read-only workspace and ephemeral writable tmpfs.
