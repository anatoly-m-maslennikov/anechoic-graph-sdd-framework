---
atom_family: TKT
atom_id: AN-T-935
container:
  atom: AN-T-942
priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 5
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Bind existing Draft promotion targets

## Objective

Seal the exact Draft descriptor, canonical predecessor descriptor, and proposed Version. Reuse typed carrier descriptors; require proposed Version=predecessor+1 and refuse stale, missing, ambiguous or colliding targets before effects.

## Details

At most 15 minutes own work; split before extending. Follow PROGRAMMATIC M projection and latest Operator same-ID promotion decision. Preserve exact history; no Journal/retained-Draft-history admission gate. No live test traffic, deployment, Methodology map repin or held-batch replay.

### Definition of Done

Seal the exact Draft descriptor, canonical predecessor descriptor, and proposed Version. Reuse typed carrier descriptors; require proposed Version=predecessor+1 and refuse stale, missing, ambiguous or colliding targets before effects. Observable focused evidence and independent review are required. Review dependent next Task before execution.

### Dependency review checkpoint

P2468 binding/preflight completed. Four frozen checks passed, including existing-marker creation, sealed-target rejection, Done-to-Active Version refusal and strict Boolean Version denial. Current uniqueness uses the shared bounded CurrentAtomLocator. API review accepts exact target and canonical_target descriptors plus explicit proposed_version; IDs/paths/Versions/digests must agree. P2469 was dependency-reviewed against these checks before activation; publication is not yet accepted.
