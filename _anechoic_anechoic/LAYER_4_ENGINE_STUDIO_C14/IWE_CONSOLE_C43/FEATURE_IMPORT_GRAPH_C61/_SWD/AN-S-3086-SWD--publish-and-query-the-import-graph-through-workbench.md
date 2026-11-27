---
atom_family: SPEC
atom_id: AN-S-3086
container:
  component: C61
tier: 2
context:
  lens: SWD
state:
  status: active
  version: 12
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---

## Summary

Publish and query the Import Graph through Workbench

## Claim

### Prose Claim

- Deliver this projection on the native Workbench query owner.
- Enable it by default. Set `runtime.workbench.import_graph` to `false` in the selected Project Manifest to disable it.
- Its optional `python_roots` is an ordered list of Project-relative roots.
- Its optional `python_image_imports` declares exact module names per
  Project-relative Python source file. Use it for execution in a previous
  runtime image. When a declared module has no local target, retain its
  occurrence and record it as a declared previous-image dependency.
- Its `include` is a list of Project-relative source files.
- Reconcile the retained import snapshot with the current Project at startup.
- Build from source when no compatible snapshot exists.
- Use one existing `SourceWatcher` observer and event queue over the selected Project.
- Do not overlap watcher roots.
- Filter watcher batches with the scan admission rules and resolve both ends of a move.
- Route import inputs and test-directory changes to this projection.
- Refresh the Atom projection for Carrier changes, including when the Import Graph is disabled. Keep Spec Trace on its existing path.
- Parse added and edited files, scan new and moved subtrees, and remove facts from deleted paths.
- Re-resolve affected occurrences from recorded specifiers when a source path or resolution input changes.
- Store admitted paths, fingerprints, scan status, parser version, and raw import sites in Workbench DuckDB.
- Retain each written Module, imported name, relative level, line, and column.
- Reuse parsed records when fingerprint and parser version match, except after a read issue.
- Retain each current source read issue with its path and message until a successful read or removal.
- On the next ordinary scan, read that source even if its fingerprint is unchanged.
- Add no automatic retry or recovery.
- Then resolve from the current inventory and configuration.
- When the Realization Graph is disabled, remove stale import facts and registration before serving queries.
- Scan and parse before taking the query lock.
- Publish each batch in one transaction on the existing Workbench DuckDB connection.
- On refresh failure, write an explicit error to stderr and discard the failed batch.
- Make no partial publication on refresh failure.
- If a failed rebuild may have lost DuckPGQ registration, leave the owner unavailable until explicit restart.
- Return the error in each failed HTTP or MCP request.
- On a full rebuild, rebuild Atom and enabled import projections from the selected sources.
- A selected table rebuild also rebuilds its dependent tables, views, and graph registration.

Publish Realization Graph relations and registration under AN-S-5171.

Refresh and publish Package audit evidence under AN-S-5172.
