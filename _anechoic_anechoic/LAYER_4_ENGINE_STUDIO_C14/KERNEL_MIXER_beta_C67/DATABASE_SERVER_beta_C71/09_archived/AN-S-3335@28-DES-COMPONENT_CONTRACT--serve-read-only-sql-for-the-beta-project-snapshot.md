---
atom_family: SPEC
atom_id: AN-S-3335
container:
  component: C71
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3333
state:
  status: "archived"
  version: 28
  updated_at: "2026-11-23T04:35:09.800901+00:00"
---
## Summary

Serve read-only SQL for the Beta Project snapshot

## Guarantee

Admit the Model, Structure, native revisions and relations, and enabled Realization Graph
in one transaction for the bound Project. Keep the prior generation on
failed admission. Serve its exact artifact bytes and one read-only SQL
SELECT per request, with no external access and at most 1,000 rows.
Keep a 16 MiB result budget in Kernel. Charge serialized result and
SQL bytes with a 4 KiB minimum for each result. Limit each serialized
result to 1 MiB. Refuse a new result or refresh
that would exceed capacity. Do not evict young or pinned results.
Pages keep their result across a generation update. Open Views pin results.
Unpinned results expire after the configured startup lifetime of 3,600
seconds by default. View result IDs and rows are transient.

When Workbench selects disk storage, retain the accepted generation in a
private database bound to the Project instance and Manifest digest. Restore
it when that binding reopens. Commit the input proof and the native
carrier paths and content hashes with the accepted generation.
On a Ticket delta, replace the affected checkpoints and remove
paths that are absent. Expose the current proof to Orchestrator.
Expose DuckPGQ queries for admitted imports
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

Own Saved SQL for the admitted Project. Store a successful Query or View
Run with a save request as a Bookmark. Save View snapshots one valid
read-only SELECT from a bound View or explicit SQL text without running it.
Use a canonical UUIDv7 and append under the Project Journal's fixed
`workbench-saved-items` author. Use the selected file or DuckDB storage.
Return the ID after the write. A failed save preserves a successful Run
and its query ID and returns a partial outcome.

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

Serve structural cycles, Package coupling, and antipattern evidence
through `import_cycles`, `package_coupling`, and `antipattern_findings`.

Accept a native-only refresh against the named current generation.
Validate the native snapshot against the admitted Model. Replace Atom
and native relation rows in one transaction. Retain Model, Structure,
and Realization Graph rows when the request contains only a native
snapshot. When the request also supplies a Realization Graph and its
digest, validate it against the admitted Structure and replace it
in the same transaction. Retain the exact Model and Structure.
Refuse a stale generation and retain the prior state on failure.

A Ticket delta names the current generation and up to 1,024 affected paths.
Publish the changed Atom rows and Model-defined relations together in one
transaction, including their graph rows.
Retain the accepted Model, Structure, and Realization Graph. Request
reconciliation when the delta cannot preserve relation ownership.

Derive Component flows from observed events. Expose their causal
links and shared-action candidates in SQL. Admit each bound trace atomically. Preserve the
event stream across generation rebuilds and disk reopen.

## References

AN-S-3333, AN-S-2242, AN-S-1356, AN-T-2958, and AN-T-2976.
