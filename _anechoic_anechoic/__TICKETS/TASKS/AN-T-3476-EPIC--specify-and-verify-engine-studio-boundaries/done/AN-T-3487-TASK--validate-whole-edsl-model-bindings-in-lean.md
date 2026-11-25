---
atom_family: TKT
atom_id: AN-T-3487
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 2
  updated_at: '2026-11-24T10:34:45.067213+00:00'
---
## Summary

Validate whole eDSL Model bindings in Lean

## Work

Use the canonical resolutions to validate the whole admitted Model in Lean, including Node, Property, and Relation bindings and their closure. Generate the validation from explicit Model declarations with zero magic; report unsupported or unresolved cases as failures.

## Acceptance

Lean validates the complete admitted Model and its bindings. Missing, ambiguous, invalid, or unbound declarations fail validation with actionable evidence.

## Findings

Lean checked all scoped structural obligations, including active and inherited bindings. It rejected a missing Node, missing base, cycle, missing Property bearer, missing Relation endpoint, and missing inverse with provenance. Callback checks remain in Python.
