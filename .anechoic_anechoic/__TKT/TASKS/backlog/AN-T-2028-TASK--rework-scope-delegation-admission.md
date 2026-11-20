---
identity:
  atom_id: AN-T-2028
context:
  container:
    component: C00
  tier: 3
  template: task
state:
  status: backlog
  version: 1
  updated_at: 2026-11-11 20:34:11 +0400
---

## Summary

Rework Scope Delegation admission

## Objective

Rework formal Scope Delegation admission for version 0.7, including allowed Roles, Forms, and Subjects.

## Work

- Review the Current Scope Delegation rules, concrete Delegations, and the CA-A-1336 Draft.
- Define and review how Delegations express and apply permissions for Roles, Forms, and Subjects.
- Update the affected declarations and implement and verify the accepted rules.

## Definition of Done

The reviewed Model and implementation agree on Scope Delegation admission for Roles, Forms, and Subjects. Evaluations cover allowed and refused cases.

## Context

The Operator deferred formal Scope Delegation admission to version 0.7. CA-C-730 records the earlier lifecycle admission question and existing evidence.
