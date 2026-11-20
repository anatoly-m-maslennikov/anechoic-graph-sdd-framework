---
atom_family: SPEC
atom_id: AN-S-1689
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: 2026-11-02 17:54:42 +0400
---

## Summary

Bind Step parameters

## Claim

### Prose Claim


Step selections and parameter bindings.


A Step **must** own the bindings for the Action or Workflow it RUNS.

Each bound value comes from one of:

- A previous Step output.
- The input of the enclosing Workflow Run.
- A fixed value declared by the Step.

A Step binding references the selected Action or Workflow contract. It does not copy or redefine that contract. Passed bindings may serve as logical switches: their values select declared behavior or routing without redefining the called contract.
