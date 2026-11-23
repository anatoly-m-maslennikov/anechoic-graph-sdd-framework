---
atom_family: SPEC
atom_id: AN-S-2752
container:
  component: C9
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 21
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Author Plan Atoms

# Summary

Author Plan Atoms

## Scope

Plan Atoms.

## Claim

**to** author a Plan Atom, apply the common Plan authoring rules independently of Label:

1. resolve **`=1`** effective Author.
2. state **`=1`** intended work **or** outcome **in** Objective, supported by own work, direct decomposition, **or** both under CA-R-1575.
3. resolve its Claim Target Scope Unit under CA-R-1588; keep narrower **or** composite work restrictions **in** Objective, **and** do **not** target an ancestor Scope Unit.
4. **if** it has own work, resolve **`=1`** effective Assignee **and** assign that work **to** that Assignee. retain the leaf-work bound under CA-R-1589.
5. write **`=1`** Definition of Done under CA-M-123, carried inside Details under CA-D-470; include decomposed completion obligations **when** applicable.
6. use a Label **only** for navigation; apply an authoring Subtype **only when** explicitly governed.
7. express required start dependencies with `BLOCKS`; declare `IS_DECOMPOSITION_OF` **only** on the decomposing Plan under CA-D-481. derive the inverse; do **not** infer execution dependencies from leading numbers **or** folder placement.
8. resolve confidence **and** retry values from their applicable sources; store **only** explicitly selected overrides on this Plan.
9. keep supporting Details within Objective **and** its restrictions **without** another intended outcome. review Objective against the completed Details **and** Definition of Done; explicitly revise Objective **if** needed **and** recheck their agreement.
10. **only after** that review, derive Summary from the finalized Objective under CA-R-1418 **and** CA-R-1465. retain the established Summary across Revisions; **if** it needs changing, replace the Atom identity under CA-R-1464.

## Details
