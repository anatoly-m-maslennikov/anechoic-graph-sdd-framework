---
atom_family: SPEC
atom_id: AN-S-2251
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: active
  version: 7
  updated_at: '2026-11-13T15:52:46.201826+00:00'
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
- exclude an ordinary source that cannot be parsed or read stably and remove any older query row for that file. Keep parseable files queryable and report violations of the current declared schema separately.
- leave unrelated valid sources queryable when another source is excluded.
- report source-file errors with path and available location information through stderr and the queryable issue tables. Publish audits asynchronously after source rows commit. Expose audit progress and the elapsed time of the most recent audit so users can identify pending diagnostics.
- skip an excluded source without automatic retry; a later actual source change may be considered on a later refresh.
- remain distinct from source deletion: a source-file error is not proof that the source was deleted.

An invalid Current Scope Unit Declaration must not produce valid or partial projected structure.

Report duplicate Atom IDs and Versions among selected Current and Archived rows. Drafts and Backlog rows are outside that duplicate check. Archive duplicate coverage is limited to the loaded folders and any exact archived files included in `atoms`.
