---
atom_family: TKT
atom_id: AN-T-3940
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-25T22:10:56+00:00'
---
## Summary

Split Spec Engine into owned child Components

## Work

Give each responsibility a child Component. C75 owns the formal chain
entry point and orchestration.

Use five dependency layers. Spec Sources and Diagnostics share L1.
Formal Model is L2. Lean Translator and Mermaid Renderer share L3.
Translation Validator and Spec Comparison share L4. Delegation
Verification is L5.

## Acceptance

Each child has a formal boundary and owns its implementation. Existing
callers and supported checks pass through the new boundaries.
