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
  version: 8
  updated_at: "2026-11-22T15:04:56.601487+00:00"
---
## Summary

Serve read-only SQL for the Beta Project snapshot

## Guarantee

Admit the Model, Structure, native revisions and relations, and enabled Realization Graph
in one transaction for the bound Project. Keep the prior generation on
failed admission. Serve its exact artifact bytes and one read-only SQL
SELECT per request, with no external access and at most 1,000 rows.
Keep up to 16 inline results of at most 1 MiB each in Kernel. Pages
keep their result across a generation update. Open Views pin results.
Unpinned results expire after the configured startup lifetime of 3,600
seconds by default. View result IDs and rows are transient.

When Workbench selects disk storage, retain the accepted generation in a
private database bound to the Project instance and Manifest digest. Restore
it when that binding reopens. Expose DuckPGQ queries for admitted imports
and Package and Component test relationships.

Keep each Workspace bound to its Project and session. Preserve View IDs
and edits across Kernel restarts independently of query storage. Refuse
stale View revisions and keep at least one View in each Workspace.

For DuckDB Work Journal storage, admit staged records into the Project's
existing Journal table. Remove an inbox record after its commit.
Refuse conflicting bytes for an accepted record ID.

## References

AN-S-3333, AN-T-2958, and AN-T-2976.
