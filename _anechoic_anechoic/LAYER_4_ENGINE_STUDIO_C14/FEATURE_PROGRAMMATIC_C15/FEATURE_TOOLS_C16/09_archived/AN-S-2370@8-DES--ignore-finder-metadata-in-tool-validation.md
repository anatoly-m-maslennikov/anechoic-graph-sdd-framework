---
atom_family: SPEC
atom_id: AN-S-2370
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 8
  updated_at: 2026-10-24 17:12:09 +0400
---
## Summary

Ignore Finder metadata in Tool validation

# Summary

Ignore Finder metadata in Tool validation

## Scope

Tool selection, persistent inventories, digests, package and Projection checks, and runtime control-directory checks at any depth.

## Claim

Tool validation **must** ignore files named `.DS_Store` so their presence, absence **or** contents do **not** change validation results.

## Details

Finder metadata is not an admitted source, package member, generated output, Skill resource, Journal event or runtime message. Exclude it before reading file contents or comparing persistent inventories; neither deleting it nor preventing Finder from creating it is a prerequisite.

This exclusion is for the exact basename `.DS_Store`. All other files retain their existing admission, ownership, missing-file, digest, mode and safety checks. Historical evidence remains unchanged; an earlier metadata-related failure retains its actual recorded outcome.
