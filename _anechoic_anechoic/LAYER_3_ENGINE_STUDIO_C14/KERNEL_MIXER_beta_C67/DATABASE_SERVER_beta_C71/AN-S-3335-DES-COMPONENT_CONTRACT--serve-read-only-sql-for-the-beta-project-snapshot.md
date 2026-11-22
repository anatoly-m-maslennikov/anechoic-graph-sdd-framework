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
  status: "active"
  version: 3
  updated_at: "2026-11-22T11:57:57.076800+00:00"
---
## Summary

Serve read-only SQL for the Beta Project snapshot

## Guarantee

Admit matching Model and Structure artifacts and the Project rows in
one transaction for the bound Project. Keep the prior generation on
failed admission. Serve its exact artifact bytes and one read-only SQL
SELECT per request, with no external access and at most 1,000 rows.

## References

AN-S-3333, AN-T-2958, and AN-T-2976.
