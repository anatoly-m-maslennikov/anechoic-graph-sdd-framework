---
atom_family: SPEC
atom_id: AN-S-258
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 9
  updated_at: 2026-09-12 04:15:38 +0400
---
## Summary

Verify generate one generic Artifact catalog

# Verify generate one generic Artifact catalog

## Claim checked

CA-M-211 materializes a deterministic non-authoritative catalog from exactly its declared authority frontier.

## Applicable when

apply whenever a catalog definition, source contribution, **or** generator changes.

## Test case

build one catalog twice from a known declared authority frontier, **then** attempt generation with a source contribution whose required ordering value is unresolved.

## Acceptance criteria

the two valid builds are byte-identical, contain **every** **and** **only** declared source contribution **in** stable order, **and** identify the source frontier **and** generator. the unresolved-ordering case produces no catalog.

## Failure disposition

reject the catalog method **and** preserve definition, source frontier, both derived outputs, unresolved-ordering finding, **and** source-to-output comparison.
