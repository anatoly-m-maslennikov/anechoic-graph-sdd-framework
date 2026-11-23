---
atom_family: SPEC
atom_id: AN-S-1143
container:
  component: C16
tier: 1
context:
  lens: SWD
state:
  status: archived
  version: 19
  updated_at: 2026-10-27 19:59:40 +0400
---
## Summary

Patch generic Artifact metadata

# Patch generic Artifact metadata

## Applicable when

use this Method **when** a governed Tool needs the shared mechanics for a field-level frontmatter patch on one generic Artifact.

## Procedure

1. resolve **=1** generic Artifact **and** seal its path, revision, digest, schema, current frontmatter, **and** body digest.
2. apply **only** declared add, replace, **or** remove operations **to** registered frontmatter fields.
3. validate the resulting complete frontmatter document **and** reject unknown fields, failed preconditions, **and** **all** relation-target operations.
4. produce the exact field-level dry-run while preserving the original body bytes **and** carrier identity.
5. on authorized apply, recheck the sealed preconditions, atomically replace the carrier, advance governed revision metadata once, **and** prove the unchanged body digest.

## Outcome

the Artifact receives one schema-valid metadata revision while its body **and** identity remain unchanged.

## Failure or stop

stop **or** roll back on stale preconditions, unknown fields, schema failure, failed body preservation, **or** **any** requested relation patch.
