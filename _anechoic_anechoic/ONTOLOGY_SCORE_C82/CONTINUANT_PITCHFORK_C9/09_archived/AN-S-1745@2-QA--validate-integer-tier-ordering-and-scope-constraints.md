---
atom_family: SPEC
atom_id: AN-S-1745
container:
  component: C9
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-10-24 02:14:24 +0400
---
## Summary

Validate Integer Tier Ordering and Scope Constraints

# Summary

Validate Integer Tier Ordering and Scope Constraints

## Scope

Current RMEDO source Atoms and their permitted Current Atom targets.

## Claim

this Evaluation **must** cover one coherent numeric graph-ordering case:

- ordinary Project-owned Atoms carry integer Tier **>=0**; ordinary non-Project Atoms carry integer Tier **>=1**; a verified Project Goal carries exactly Tier **-1**;
- the integer Tier is independent of Content Role, Type, semantic abstraction, Claim Scope breadth, filename, structural depth, and any named category;
- for every stored governing Current R/M/E/D relation occurrence selected under CA-R-2148, a same-Scope target has a strictly lower Tier than its source;
- a strict-ancestor target is permitted without Tier comparison; descendant and sibling targets are forbidden;
- the source endpoint is Current R/M/E/D, while the target may be any Current Atom permitted by the registered relation endpoint definition;
- valid existing integers are preserved, and a source integer may be raised when required by the same-Scope ordering and admitted owner range;
- unknown relation membership or endpoints, missing Tier/scope/parentage, derived inverse views, and cycles are unresolved failures, not silent passes.

No Content-Role or Type-to-Tier restriction is introduced by this case.

