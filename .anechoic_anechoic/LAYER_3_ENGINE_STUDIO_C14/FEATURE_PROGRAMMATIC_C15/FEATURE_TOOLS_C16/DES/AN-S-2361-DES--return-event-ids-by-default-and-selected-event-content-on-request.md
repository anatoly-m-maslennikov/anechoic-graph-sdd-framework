---
identity:
  atom_id: AN-S-2361
context:
  container:
    component: C16
  tier: 3
  lens: DES
state:
  status: active
  version: 9
  updated_at: 2026-11-02 19:44:26 +0400
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
