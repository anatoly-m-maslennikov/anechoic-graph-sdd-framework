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
  status: archived
  version: 20
  updated_at: '2026-11-22T18:31:13.925650+00:00'
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

Filter, sort, and group retained inline results before paging. On an
explicit result refresh, issue replacement IDs and update any View pins
in the same locked operation. For a projection rebuild, commit the new
generation and its result refresh together. Keep the prior generation
and result IDs if capture fails.

For file Journal storage, read the admitted Project-relative Journal
directory into a connection-local `work_journal` projection before SQL.
Keep the prior rows if a carrier cannot be validated.

Record query and View Run attempts through one ordered background writer
per Project owner. Retain their seven technical fields for 48 hours in
hourly UTC files. Expose the same retained attempts through read-only
list, get, and `query_log` SQL. Check creates no attempt. A log failure
leaves the Run response intact. Drain the writer on orderly shutdown.

Return public schema fields and available distinct Status values from the
same accepted generation. Omit hints outside the supported bound.
Schema reads create no technical query attempt.

Load saved SQL by its admitted Project ID. List bounded metadata without
SQL bodies. Read compatible historical files and accepted DuckDB records
across Journal storage changes. Saved reads do not alter their carriers.

Deliver cached results inline or as disposable files under the admitted
Project. Export the whole accepted Run or the requested Page or View
Fetch as JSON matrix, CSV, or TOON. Preserve positional values and
column names. Return a partial outcome with the existing query ID when
an export fails. Keep the result available for later reads.

Apply a Run preview cap before materializing the result. Apply a Page
or View Fetch preview only to the delivered page. Preserve the Run
preview cap when refreshing the retained result.

Publish admitted Code Access findings with the Realization Graph. Keep
declared owner bypasses visible. Omit the graph tables when disabled.

Publish `code_units` and `code_unit_calls` in the same generation.
Expose Module membership and calls through DuckPGQ. Retain the source
Module on propagated effects.

Accept a native-only refresh against the named current generation.
Validate the native snapshot against the admitted Model. Replace Atom
and native relation rows in one transaction. Retain Model, Structure,
and Realization Graph rows. Refuse a stale generation.

A Ticket delta names the current generation and the affected paths. Update
the Atom rows and Model-defined relations for those paths in one transaction.
Retain the accepted Model, Structure, and Realization Graph. Request
reconciliation when the delta cannot preserve relation ownership.

## References

AN-S-3333, AN-S-2242, AN-S-1356, AN-T-2958, and AN-T-2976.
