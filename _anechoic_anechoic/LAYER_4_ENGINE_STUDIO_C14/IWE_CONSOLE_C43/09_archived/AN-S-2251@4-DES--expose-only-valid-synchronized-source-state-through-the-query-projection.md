---
atom_family: SPEC
atom_id: AN-S-2251
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-09 00:09:26 +0400
---
## Summary

Expose only valid synchronized source state through the query Projection

## Claim scope

The correspondence between selected governed Atom sources and their query Projection rows.

## Claim

### Prose Claim

The query Projection **must**:

- expose a complete committed state from valid selected sources.
- make valid selected sources available without exposing a partial update.
- exclude an invalid, unreadable, or unstable ordinary Atom source and its derived data; an older state of that source **must not** remain queryable as current.
- leave unrelated valid sources queryable when another source is excluded.
- report a source-file error, with its path and available location information, through stderr rather than as a result row.
- skip an excluded source without automatic retry; a later actual source change may be considered on a later refresh.
- remain distinct from source deletion: a source-file error is not proof that the source was deleted.

An invalid Current Scope Unit Declaration must not produce valid or partial projected structure.
