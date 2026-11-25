---
atom_family: TKT
atom_id: AN-T-3491
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 2
  updated_at: '2026-11-25T15:41:06+00:00'
---
## Summary

Migrate or add formal Contracts for all Project Components

## Work

For every Project Component in the live declared inventory at execution
time, migrate existing Contract claims into the formal eDSL or add a
formal Contract with a current Manifest link. Reuse valid formal
Contracts. Treat Component Seeds as a separate entity.

Include Engine Studio (C14), Release (C27), User Setup (C65), and all
their declared descendants in the formal-spec cycle.

## Acceptance

Each Project Component has a formal Contract linked to its current Manifest, or has a specific evidence-backed unresolved gap left open. Report the live inventory coverage, reused Contracts, and exact links; do not rely on a fixed prior count.

## Open boundaries

- C31 and C32 have declared child groups. The Atom Action rule applies
  to one explicit Atom target. General scheduling behavior still needs
  an accepted boundary.
- The C33 Workflows declarations are archived. C18 owns Workflow
  sequencing under AN-S-2481@25.
- C36 remains declared for Scope Unit Actions. Its action boundary
  needs an accepted definition. C18 owns the CreateScopeUnit Workflow.
- C38–C40 have declared names and parents. The Journal, Project,
  and Queue Action inputs and effects still need an accepted boundary.
- C41 and C42 are separate scheduler Components under C32. Their
  Active declarations establish identity and containment. A callable
  operation, its input, result, effects, and failure rules need an
  accepted definition. C18 owns Workflow sequencing for explicit
  Atom Actions. The Active Specs leave scheduling ownership open.
- C60 needs an explicit purpose and boundary. Its Manifest permits
  the SPEC Lens.
- C910647071 has a Draft Contract and Decision for its retained
  Workbench fixture population. All 500 Current sources match the
  recorded Git baseline. Any behavior beyond fixture retention
  remains open.
