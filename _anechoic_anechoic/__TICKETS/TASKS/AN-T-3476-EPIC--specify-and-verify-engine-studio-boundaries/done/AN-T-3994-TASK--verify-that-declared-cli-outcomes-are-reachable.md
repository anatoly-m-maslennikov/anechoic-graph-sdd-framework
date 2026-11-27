---
atom_family: TKT
atom_id: AN-T-3994
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T02:35:43.705521+00:00"
---
## Summary

Verify that declared CLI outcomes are reachable

## Acceptance

Use guard reachability when checking declared exit codes. Reject a success branch that requires incompatible literal and bound values. Report unresolved when feasibility cannot be established. Keep an executable Lean replay with feasible success and failure controls.

Respect the Contract's exit class. Prove that reachable failures with
exit codes 1 and 2 both satisfy a nonzero guarantee. A zero failure must
conflict. Check exact exit codes when the Contract declares them.
