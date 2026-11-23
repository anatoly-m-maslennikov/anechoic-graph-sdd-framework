---
atom_family: SPEC
atom_id: AN-S-1100
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Verify capture one external source

# Verify capture one external source

## Claim checked

CA-M-213 captures one immutable external source carrier with complete provenance **and** an explicit reproducibility result.

## Applicable when

apply whenever external-source capture **or** provenance-carrier mechanics change.

## Test case

capture one supplied external text with origin, retrieval time, attribution, **and** content digest. attempt a second capture lacking attribution **and** inspect both outcomes.

## Acceptance criteria

the valid capture creates one immutable carrier whose bytes match its digest **and** records the required provenance **and** reproducibility outcome. the incomplete capture produces no carrier **and** no invented provenance.

## Failure disposition

reject the source-capture method **and** preserve both capture inputs, carrier bytes, digest comparison, recorded provenance, reproducibility result, **and** rejection evidence.
