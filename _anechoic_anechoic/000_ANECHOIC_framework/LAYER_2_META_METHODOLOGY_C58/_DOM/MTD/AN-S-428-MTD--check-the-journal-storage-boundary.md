---
atom_family: SPEC
atom_id: AN-S-428
container:
  component: C58
tier: 3
context:
  lens: DOM/MTD
state:
  status: "active"
  version: 25
  updated_at: "2026-11-25T23:08:32.349559+00:00"
---
## Summary

Check the Journal storage boundary

## Claim

Check plain append, read, and storage under AN-S-1821.

## Details

- Append observations of valid and invalid Project state, including failed or unresolved evaluations. Read them back as supplied. Changes to the live Project preserve earlier observations.
- Append identical observations twice and then append a different payload using the same observed ID. Verify each explicit append preserves its supplied row and order.
- Check an encoding failure, a read or write failure, denial of unauthorized access, and an attempted overwrite. Report the actual failure and any observed partial append. Preserve accepted history.
- Check Project conformance and authorization for a source action separately.
