---
atom_family: TKT
atom_id: AN-T-3971
container:
  atom: AN-T-3968
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-26T05:13:50.810810Z'
---

## Summary

Verify and release the merged stack

## Work

Run the affected Model, lifecycle, Spec Engine, Workbench, and Realization Graph checks. Complete Local Release and verify production MCP on port 7777. Commit and push the release and Ticket updates.

## Verification

Local Release merge-epic-04476 passed 45 Static checks, 821 Functional tests, 33 image tests, 14 canary support tests, and a real Project MCP canary. OrbStack serves version 0.4.4.76 from cf44b0a440 on port 7777.

Production MCP returned 5,487 containment edges and 6,602 Archive maxima. The Project can load with 104 undeclared IS_REFERENCE warnings. The merged Realization Graph reports 257 denied imports. [AN-T-3978](../../../../ISSUES/AN-T-3978-QUESTION--reconcile-code-access-after-the-ontology-merge.md)

MCP refused the status change at the DuckDB query memory limit, with no effects. The Operator authorized the in-place fallback. [AN-T-3979](../../../../ISSUES/AN-T-3979-PROBLEM--bound-ticket-status-context-memory-on-full-projects.md)
