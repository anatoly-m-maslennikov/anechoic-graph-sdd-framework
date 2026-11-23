---
atom_family: SPEC
atom_id: AN-S-1715
container:
  component: C9
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 13
  updated_at: 2026-10-29 07:45:29 +0400
---
## Summary

Derive Current RMED Atom Ordering Tier

## Claim scope

Current RMEDO Atoms and the stored governing relation occurrences that constrain their integer Tier.

## Claim

to derive one Current R/M/E/D Atom's integer Tier, the Author **must**:

1. resolve the complete Atom Claim and actual owner. For an ordinary endpoint resolve its Local Scope Unit; for a verified Operator-owned Project Goal resolve its Target Project as the ordering context under CA-D-637, without changing its Actor owner. Resolve declared ancestry for these contexts;
2. select only stored governing RMED relation occurrences under CA-R-2148. The source endpoint **must** be a Current R/M/E/D Atom, and the target endpoint **may** be any Current Atom permitted by that relation's endpoint definition;
3. preserve a valid existing integer Tier. Ordinary Project-owned Atoms use Tier **>=0**, ordinary non-Project Atoms use Tier **>=1**, and a verified Project Goal uses exactly Tier **-1**;
4. for each selected same-Scope occurrence, require the target Tier to be strictly lower than the source Tier; for a target in a strict ancestor Scope Unit, accept the occurrence without comparing Tiers; for a source and target that resolve within the same Project to the Project Configuration source role and its Core Meta-Model prerequisite role declared by CA-R-1218, accept the occurrence without comparing Tiers;
5. treat every other descendant or sibling target, unknown relation membership or endpoints, missing Tier/scope/parentage, unresolved logical-role identity, unresolved Project correspondence, an unresolved CA-R-1218 prerequisite declaration, derived inverse views, and cycles as unresolved failures rather than silently passing them. Where the approved ordering requires it and the owner range permits it, raise the source integer Tier until the same-Scope constraint holds.

Tier is a graph-ordering level only. It does not classify semantic abstraction, importance, Claim Scope breadth, Content Role, Type, Source ownership, filename, structural depth, or any named tier category.
