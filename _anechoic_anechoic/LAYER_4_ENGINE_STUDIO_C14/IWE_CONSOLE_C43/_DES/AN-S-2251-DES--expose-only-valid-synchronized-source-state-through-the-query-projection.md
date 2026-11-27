---
atom_family: SPEC
atom_id: AN-S-2251
concern:
  subject: "Projection"
  path: "Model/Graph/Node//Artifact//Derived"
  relation: "is_narrower_than"
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: active
  version: 10
  updated_at: "2026-11-27T17:35:01.150345+00:00"
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
- Report source-file errors to stderr with path and available location information. Apply AN-S-1944 and AN-S-1948 for query-visible issues and audit state and AN-S-1967 for asynchronous audit publication.
- skip an excluded source without automatic retry; a later actual source change may be considered on a later refresh.
- remain distinct from source deletion: a source-file error is not proof that the source was deleted.

Use the Atom ID, Status, and Container from the Header. A parent’s Status does not set a child’s Status. Keep parseable Atoms with placement discrepancies indexed under their declared Containers. Report the Atom reference and its actual and expected paths. A requested Active Atom requires exactly one match. Report an absent or ambiguous match.

An invalid Current Scope Unit Declaration must not produce valid or partial projected structure.

Apply AN-S-1967 to duplicate Atom ID and Version checks. Archive coverage includes only loaded folders and exact archived files included in `atoms`.
