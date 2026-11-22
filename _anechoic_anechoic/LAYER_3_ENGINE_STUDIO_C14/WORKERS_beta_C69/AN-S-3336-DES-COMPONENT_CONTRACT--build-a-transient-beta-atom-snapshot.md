---
atom_family: SPEC
atom_id: AN-S-3336
container:
  component: C69
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: "active"
  version: 1
  updated_at: "2026-11-22T11:21:07.088380+00:00"
---
## Summary

Build a transient Beta Atom snapshot

## Guarantee

Given a pinned native Project binding, read the Current Atoms and emit
their references and summaries in reference order. Include the pinned
Manifest digest. Refuse an invalid binding, changed Manifest, or capture
with errors. The worker exits after writing its result.

## References

AN-S-3334, AN-T-2958, and AN-T-2976.
