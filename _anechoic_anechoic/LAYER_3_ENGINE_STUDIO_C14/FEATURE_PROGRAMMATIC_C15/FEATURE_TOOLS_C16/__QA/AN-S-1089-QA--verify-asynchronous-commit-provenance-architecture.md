---
atom_family: SPEC
atom_id: AN-S-1089
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Verify asynchronous commit-provenance architecture

# Verify asynchronous commit-provenance architecture

## Claim checked

CA-M-182 realizes CA-R-802 through one pure decision manager, one mechanical recoverable Scheduler, atomic non-deciding workers, durable state, **and** one serialized Git boundary.

## Test case

inspect the exact source frontier **and** run a controlled plan whose ready worker succeeds, whose completion is delivered twice, whose service stops **before** the next dispatch, **and** whose fixture attempts one undeclared transition **and** one second concurrent Git claim.

## Acceptance criteria

the manager performs no I/O **and** returns the same typed plan for equal inputs. **only** declared steps become ready. repeated completion is idempotent. restart resumes the persisted plan. the undeclared transition **and** second Git claim are rejected **without** mutation. no worker selects downstream work, **and** COMMIT_CHANGE_SET neither imports nor invokes a peer Tool.

## Failure disposition

reject the realization **and** preserve the first impurity, discretionary worker decision, undeclared transition, lost state, duplicate effect, peer orchestration, **or** concurrent Git mutation as a blocked architecture discrepancy.
