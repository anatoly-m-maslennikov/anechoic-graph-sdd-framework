---
atom_family: SPEC
atom_id: AN-S-257
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

Verify project bounded work journal ndjson to toon

# Verify project bounded work journal ndjson to toon

## Claim checked

CA-M-206 produces a reproducible lossless TOON Projection of one unchanged bounded Journal frontier.

## Applicable when

apply whenever the Journal-to-TOON encoder, frontier grammar, **or** Projection metadata changes.

## Test case

select a known ordered NDJSON event range, project its unchanged sealed frontier twice, **and** compare decoded values, identities, order, source frontier, encoder provenance, **and** output bytes. **then** change one selected source line between sealing **and** publication.

## Acceptance criteria

both unchanged runs are byte-identical **and** decode **to** **every** original event field **in** original order; metadata identifies the exact source frontier **and** encoder; the changed-frontier run produces no accepted Projection.

## Failure disposition

reject the Projection method **and** preserve source **and** output digests, decoded comparisons, provenance metadata, **and** changed-frontier handling.
