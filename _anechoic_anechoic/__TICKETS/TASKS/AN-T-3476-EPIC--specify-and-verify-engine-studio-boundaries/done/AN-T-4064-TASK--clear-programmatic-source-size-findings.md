---
atom_family: TKT
atom_id: AN-T-4064
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-27T11:55:15+00:00'
---

## Summary

Clear Programmatic source size findings

## Acceptance

Clear the 300-line module and 45-line function findings outside Spec
Engine. Preserve supported behavior, existing tests, and Code Access.
Verify the updated modules with focused tests and the source-size scan.
Coordinate the Spec Engine findings with AN 1.

## Evidence

Cleared all eight size findings outside Spec Engine. Refactored
validation and Journal writes without changing public interfaces.
Split existing source tests while preserving all 21 test cases and
their discovery. The focused final run passed 86 tests.

The Programmatic scan reports zero size findings outside Spec Engine.
Code Access comparison reports zero added findings. The ten remaining
Spec Engine size findings are with AN 1.
