---
atom_family: SPEC
atom_id: AN-S-3335
container:
  component: C71
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-22T11:41:29.694914+00:00"
---
## Summary

Serve read-only SQL for the Beta Project snapshot

## Guarantee

Load the supplied Atom snapshot only when its Manifest digest matches
the Project binding. Serve one read-only SELECT per request with no
external access. Return column names and at most 1,000 rows of JSON
scalars. Refuse requests for a different instance.

## References

AN-S-3333, AN-T-2958, and AN-T-2976.
