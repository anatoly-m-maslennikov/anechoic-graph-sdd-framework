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
  version: 5
  updated_at: "2026-11-22T13:27:16.400219+00:00"
---
## Summary

Serve read-only SQL for the Beta Project snapshot

## Guarantee

Admit the Model, Structure, Project rows, and enabled Realization Graph
in one transaction for the bound Project. Keep the prior generation on
failed admission. Serve its exact artifact bytes and one read-only SQL
SELECT per request, with no external access and at most 1,000 rows.
Keep up to 16 inline results of at most 1 MiB each in the owning
Project Kernel. Pages continue to read the same result after a
generation update.

## References

AN-S-3333, AN-T-2958, and AN-T-2976.
