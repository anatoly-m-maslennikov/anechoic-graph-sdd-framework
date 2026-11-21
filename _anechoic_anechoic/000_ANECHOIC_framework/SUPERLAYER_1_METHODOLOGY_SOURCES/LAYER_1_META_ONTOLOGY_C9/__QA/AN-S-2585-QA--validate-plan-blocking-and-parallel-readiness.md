---
atom_family: SPEC
atom_id: AN-S-2585
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: active
  version: 24
  updated_at: 2026-11-04 16:52:59 +0400
---
## Summary

Validate Plan blocking and parallel readiness

## Claim

### Prose Claim


Plan blocking **and** parallel readiness.


the blocking Evaluation **must** reject a start **unless** **all** explicit blockers are Done **and** the applicable execution permissions hold.

## Details

- `A BLOCKS B`, `B BLOCKS C`: permit `A`, **then** `B`, **then** `C` **only** **after** the preceding Plan is Done.
- `A BLOCKS C`, `B BLOCKS C`: allow `A` **and** `B` **to** be ready concurrently; `C` waits for both.
- reorder leading navigation numbers **or** give two Plans the same Hub: do **not** invent another blocking edge.
- reject a self-edge, cycle, unresolved **or** non-Plan target, duplicate direct declaration, independently authored `BLOCKS` inverse fact, **or** Plan scheduling encoded as `depends_on`; accept a valid derived `BLOCKS` view from a direct `IS_BLOCKED_BY` fact authored on the dependent Plan.
- accept a Done blocker; Backlog, Active, Canceled, **and** Archived **must not** satisfy its completion gate.
- combine contained-Plan terminal prerequisites (Done **or** Canceled; mixed statuses allowed) with blocking for deadlock detection: **if** containing Plan `H` contains Plan `A` **and** `H BLOCKS A`, reject the unsatisfiable cycle even though the blocking graph alone is acyclic. `IS_CONTAINED_BY`/derived `CONTAINS` does **not** establish `BLOCKS` by itself.
- distinguish readiness from forced execution: a deterministic display order does **not** prohibit concurrent independent work **or** grant execution authority.

report the failing endpoints **and**, for a cycle, its complete prerequisite chain.
