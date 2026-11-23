---
atom_family: SPEC
atom_id: AN-S-2788
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 31
  updated_at: 2026-10-30 15:57:23 +0400
---
## Summary

Define Subject Path

## Claim scope

A canonical Subject path identifying a governed or dependency target.

## Claim



The following interpretation is required when this governed concept is used:

A Subject Path is a full canonical expression identifying one thing or topic addressed by GOVERNS or DEPENDS_ON. Entity is the canonical expression root under CA-R-1248; this Definition does not enumerate a closed root-branch set. A source path retains the declared operators and full qualification; a short display label is not another identity or alias.

The target is selected by the meaning addressed, not by the Atom's Local Scope Unit, Content Role, folder or Carrier. The path names a target; it is not itself the Subject Relation. A defining Atom may introduce that target, so format checks do not require prior target existence.

## Semantics

A path may address classification without declaring an Entity kind. `Atom.Content Role` addresses the relative Property, while `Atom/(.Content Role: Plan)` identifies a qualified Atom inheriting applicable Atom features and constraints. Neither form invents an intermediate Entity kind. The root and operators follow the adopted Entity syntax under CA-R-1931; no Project-name namespace layer is introduced.
