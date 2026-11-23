---
atom_family: SPEC
atom_id: AN-S-1097
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-27 19:59:32 +0400
---
## Summary

Verify patch generic Artifact metadata

# Verify patch generic Artifact metadata

## Claim checked

CA-M-208 applies **only** schema-valid generic Artifact frontmatter patches while preserving body, identity, **and** atomicity.

## Applicable when

apply whenever generic frontmatter patch mechanics **or** schemas change.

## Test case

seal one Artifact with known body bytes. request one valid field change together with one unknown field; observe apply, **then** remove the unknown field **and** apply the sealed valid patch.

## Acceptance criteria

the invalid patch changes nothing; the valid patch changes **only** the declared frontmatter field, advances revision once, **and** preserves body bytes, path, filename, **and** identity.

## Failure disposition

reject the realization **and** preserve schema, patch operations, exact diff, revision, **and** body digest.
