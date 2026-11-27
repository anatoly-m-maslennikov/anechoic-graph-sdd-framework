---
atom_family: SPEC
atom_id: AN-S-2361
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 9
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Return Event IDs by default and selected Event content on request

## Scope

The Event result representation.

## Claim

### Prose Claim

FIND_AND_FETCH_JOURNAL_EVENTS **must** return canonical Event IDs only unless the caller explicitly requests selected Event fields or complete Events.

## Details

Selected fields retain caller order and values; complete Events retain canonical Event bytes/structure. Missing selected fields are reported per Event and never silently synthesized.
