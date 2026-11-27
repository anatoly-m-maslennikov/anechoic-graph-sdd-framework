---
atom_family: SPEC
atom_id: AN-S-2250
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 8
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Derive the query Projection only from governed Atom sources

## Claim scope

The query Projection of governed Atom carriers, including selected Archive folders.

## Claim

### Prose Claim

The query Projection **must**:

- index Current, Draft and Backlog Atom carriers at Workbench startup.
- load Archive contents on demand for one or more requested Scope Unit and Role pairs. Resolve each pair to the model-declared Archive folder and its admitted aliases. Add the selected Archive rows to `atoms` and report the loaded scope coverage. A new Workbench owner starts without loaded Archive scopes.
- keep separate rows for physical files using Project-relative path and filename. A repeated load must not duplicate a physical file.
- reserve Archive IDs and Versions from filename metadata while content rows are unloaded. Expose the highest Archived Version only for Atom IDs with a Current Atom or Draft, and the highest Archived Atom number per Role across all eligible Archive filenames. Apply the configured allocation range when choosing a new ID. If an exact historical selector or safe allocation needs an unloaded Archive, report that it is unloaded separately from a missing revision. A lifecycle operation may read an exact newly archived file it already identifies.
- retain each indexed carrier's source locator, Atom identity, Version, lifecycle group, parsed Header, Markdown Content, and mapped Content Properties.
- make each source-derived Projection row include a hash for that row's complete Projection data.
- include every Current carrier regardless of its status, including Done and Canceled, and keep Current and Draft groups distinct. A carrier in one group **must not** overwrite a carrier in another group solely because they share a base ID.
- derive current Scope Unit structure only from Current Scope Unit Declarations. Draft Declarations remain queryable Atoms but do not establish Current structure. Parse source YAML and Markdown directly; no Declaration-to-reader-schema compiler is required.
- treat an observed Atom identity and Version as source data, not as a fixed-file pin or proof of a Journal record.
- remain derived data that can be rebuilt from its sources.
- never edit, move, archive, promote, or invent a source Atom.
