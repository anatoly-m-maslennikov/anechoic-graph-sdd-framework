---
atom_family: TKT
atom_id: AN-T-4053
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: "2026-11-27T10:48:07+00:00"
---
## Summary

Verify Programmatic formal Specs locally

## Acceptance

Inventory the Programmatic Component Manifests, Contracts, and Solutions. Exclude C75 Spec Engine and its children. Check exact source pins and run the local Lean verifier for supported pairs. Record conflicts and missing or unsupported comparisons.

## Evidence

Inventoried 20 Active Component Manifests. Fourteen lack an embedded
Contract, five have prose Contracts, and C30 has a raw Lean Contract.
None has an exact-bound formal Solution.

Checked 21 principal Draft Action or profile rows in local Lean. Twelve
matched, one matched on 133 bounded framing witnesses, six stayed
unresolved, and two stopped at source binding. Five raw Lean claims
typechecked. A retained C16 Draft gave one additional unresolved result.

C31 and C32 lack an admissible pairing. C15's Draft CFEL outcome differs
from the Active Python-only Contract and the running compiler. C16's
indexed CLI succeeds after its fixture Manifest is removed. Record that
difference against the older lifecycle Decision AN-S-3364@2. The Draft
comparisons do not establish Active implementation conformance.
