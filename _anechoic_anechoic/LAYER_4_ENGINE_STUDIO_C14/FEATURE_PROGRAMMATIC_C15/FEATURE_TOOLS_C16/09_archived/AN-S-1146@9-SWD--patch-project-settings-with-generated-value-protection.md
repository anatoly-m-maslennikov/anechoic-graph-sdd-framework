---
atom_family: SPEC
atom_id: AN-S-1146
container:
  component: C16
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 9
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Patch Project Settings with generated-value protection

# Patch Project Settings with generated-value protection

## Applicable when

use this Method **when** a caller supplies a bounded key-level patch for the canonical Project Settings carrier.

## Procedure

1. resolve the single canonical Project Settings carrier, its schema, current digest, **and** the requested key-level patch.
2. classify **every** target key from the settings schema as editable, generated, **or** unknown.
3. reject writes **to** generated **or** unknown values **and** preserve **all** unrelated settings exactly.
4. validate the complete resulting settings document **and** expose the exact key-level **and** byte-level dry-run.
5. on authorized apply, recheck the source digest, replace the carrier atomically, **and** prove that **only** approved keys changed.

## Outcome

Project Settings contain exactly the approved schema-valid changes while generated **and** unrelated values remain untouched.

## Failure or stop

stop on multiple settings carriers, schema failure, stale input, generated **or** unknown targets, **or** **any** undeclared diff.
