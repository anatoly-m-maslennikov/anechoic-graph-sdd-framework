---
atom_family: SPEC
atom_id: AN-S-1946
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T01:42:16.653120+00:00'
---

## Summary

Expose physical carrier mismatches

## Claim

### Prose Claim

For every selected Atom source that exists at scan time, including loaded Archives, compare its actual filename and location with the declared `file.name` and `file.path`. Expose each mismatch as one query-visible audit row with the Atom identity, the actual source path, the declared values, issue category `physical_carrier_mismatch`, and the observed and expected values. If a source disappears, remove its previous issue row on the next scan; do not claim an actual path for a file that no longer exists. Do not repair, move or rename files.

