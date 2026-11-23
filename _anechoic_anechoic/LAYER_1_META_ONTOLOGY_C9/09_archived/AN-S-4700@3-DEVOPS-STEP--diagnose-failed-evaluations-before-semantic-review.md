---
atom_family: SPEC
atom_id: AN-S-4700
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 3
  updated_at: '2026-10-21T23:29:13+00:00'
---
## Summary

Diagnose failed Evaluations before semantic review

# Summary

Diagnose failed Evaluations before semantic review

## Operation

This Step invokes CA-O-089 in Isolated context with the exact candidate, failed output, selected existing Plan or actual admitted in-session P/task including instruction/Definition of Done/source context, complete prepared tests/checks, phase, R/E/D and M bindings, relevant inputs, confidence/permission gates, and report/run bindings. CA-O-089's input and semantics remain unchanged.

Retain and pass its six possible results unchanged: `expected_initial_failure`, `implementation_defect`, `test_implementation_defect`, `authority_change_required`, `environment_blocker`, and `unresolved`. Do not edit code, tests, expected behavior, Atoms, or status.

## Details

No hidden retry or repair route and no unsupported subagent promise. The Workflow's semantic Step applies the explicit result mapping and retains failed checks, findings, blockers, and uncertainty.
