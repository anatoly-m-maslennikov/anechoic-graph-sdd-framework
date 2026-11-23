---
atom_family: SPEC
atom_id: AN-S-1196
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 26
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Bind proof records to dependency frontiers

# Summary

Bind proof records to dependency frontiers

## Scope

governed proof records, their applicable inputs, and all selected Workflows, release policies, and version-control mechanisms.

## Claim

**every** governed proof record **must** bind its observation **to** the exact applicable inputs under which it was produced.

- the binding includes the relevant Artifact **and** Implementation Revisions, configuration, evaluators, environments, **and** material inputs; CA-D-329 governs its representation.
- reliance on that observation for a current candidate requires a matching input binding **and** satisfaction of its additional governing invalidation conditions.
- a changed material input makes the affected proof stale for that candidate **until** the required checks run against the changed inputs. a missing **or** unresolved binding is unknown, **not** current.
- an unrelated change does **not** invalidate proof **unless** it changes the evaluated dependencies **or** satisfies an additional governing invalidation condition.
- retain the historical record unchanged. **not** (a recent timestamp **or** a refreshed Projection) alone proves currentness.

## Details
