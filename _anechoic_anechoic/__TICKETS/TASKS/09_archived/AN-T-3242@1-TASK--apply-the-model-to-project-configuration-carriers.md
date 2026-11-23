---
atom_family: TKT
atom_id: AN-T-3242
container:
  component: C00
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 1
  updated_at: 2026-09-12 23:54:02 +0400
---
## Summary

Apply the model to Project Configuration carriers

# Apply the model to Project Configuration carriers

the Assignee **must** apply the reconciled model **to** Project Configuration Properties **and** Relations.

## Scope

(selected RMEDO carriers **in** PROJECT_CONFIGURATION at `.anechoic_framework/00_APPLICABLE_METHODOLOGY/000_APPLICABLE_MTHD_sources/003_PROJECT_CONFIGURATION`); the source **and** lifecycle admission boundary established by CA-P-976 applies; historical versions, generated copies, runtime, Implementation code, **and** other CAP Atoms are excluded.

## Definition of Done

the Task is **not** Done **if** ((a selected Carrier uses obsolete temporal **or** role/type representation) **or** (an extension-**only** configuration boundary is broken) **or** (references **or** Subject targets are lost **or** duplicated)).

## Details

perform source Carrier normalization using the passed Core Meta-Model. finalize relevant configuration registrations, **not** unrelated P work. keep project **and** framework Settings values unchanged **and** preserve exact historical versions. generated copies are **not** source edit targets.

execute **only** **after** the explicit prerequisite is Done. **if** confidence **in** a decision is below the effective Autonomous Confidence Threshold, check Project Principles first **and** ask the Operator **if** uncertainty remains; do **not** silently select a new design. no migration is executed merely by creating this Task.
