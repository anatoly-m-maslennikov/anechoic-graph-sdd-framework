---
atom_family: SPEC
atom_id: AN-S-1950
structure:
  container:
    component: C14
  tier: 3
context:
  lens: SWD
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:56:10.799172+00:00'
---
## Summary

Keep automatic Atom numbering in the configured range

## Claim

### Prose Claim

When Project Settings provides `artifacts.identity.automatic_number_ceiling`, allocate the next number for the Role within `1` through that ceiling. Use the highest in-range number reserved by a Current, Draft or Archived carrier, including Archives whose bodies are not loaded. Treat leading zeros numerically for allocation and preserve their exact spelling in references. Existing IDs above the ceiling remain valid and addressable. Reject a new allocation if the configured range is exhausted. Without a ceiling, retain the unbounded per-Role sequence. ANECHOIC sets the ceiling to 999999 so retained throughput probes and the IDs that followed them do not advance ordinary numbering.
