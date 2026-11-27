---
atom_family: SPEC
atom_id: AN-S-188
container:
  component: C16
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 18
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Project bounded Work Journal NDJSON to TOON

# Project bounded Work Journal NDJSON to TOON

## Applicable when

use this Method **when** a bounded Work Journal frontier **must** be represented as a compact TOON Projection.

## Procedure

1. resolve an exact Journal file, event range, **or** sealed event frontier **and** record its ordered source identities **and** digests.
2. parse **every** NDJSON line strictly **and** reject malformed, duplicate, **or** changed input **before** projection.
3. encode the same ordered event values into TOON **without** adding authority, interpretation, **or** omitted fields.
4. attach the source frontier, encoder identity **and** version, **and** output digest **to** the Projection metadata.
5. decode **or** independently compare the result **to** prove lossless identity, value, **and** order preservation.

## Outcome

one reproducible non-authoritative TOON Projection represents the exact bounded Journal frontier losslessly.

## Failure or stop

produce no Projection **when** the frontier changes during generation, **any** line is malformed, **or** the result cannot be proven lossless.
