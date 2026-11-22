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
  version: 7
  updated_at: "2026-11-22T14:22:44.904464+00:00"
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

When Workbench selects disk storage, retain the accepted generation in a
private database bound to the Project instance and Manifest digest. Restore
it when that binding reopens. Expose DuckPGQ queries for admitted imports
and Package and Component test relationships.

Keep each Workspace bound to its Project and session. Preserve View IDs
and edits across Kernel restarts independently of query storage. Refuse
stale View revisions and keep at least one View in each Workspace.

## References

AN-S-3333, AN-T-2958, and AN-T-2976.
