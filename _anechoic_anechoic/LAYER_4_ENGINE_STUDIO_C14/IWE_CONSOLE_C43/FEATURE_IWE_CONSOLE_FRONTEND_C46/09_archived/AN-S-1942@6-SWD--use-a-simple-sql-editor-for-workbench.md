---
atom_family: SPEC
atom_id: AN-S-1942
container:
  component: C46
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 6
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary

Use a simple SQL editor for Workbench

## Claim scope

Workbench SQL editing, schema completion and query actions.

## Claim

### Prose Claim

Use CodeMirror 6 with its SQL language support for a text-only SQL editor and read-only completion from query_schema({}) metadata. The metadata shape is tables.atoms with name, type and optional values; tables.scope_units with name and type; and the technical read-only tables.change_log with exactly observed_at, operation, old_path and new_path. Complete actual atoms, scope_units and declared content.* columns only. Content names keep dots between path levels and snake_case within each segment, such as content.claim.prose_claim and content.claim.formal_claim; quote resulting SQL identifiers as needed and do not expose space-based Content names. Do not read saved SQL files to build suggestions.

A View contains one query. Preserve quoted strings, comments and CTEs, reject multiple SQL statements instead of selecting a statement at the cursor, and send the whole current View query plus its UTF-16 cursor position only as editing context. CodeMirror supplies editing, highlighting and completion; do not add a homegrown SQL parser, a second statement selector or SQL validation in this method. Run and Check target the whole current View query and do not save. Cmd+Enter invokes Run and Shift+Cmd+Enter invokes Check. Run & Save saves only after a successful Run, and Save View saves the whole current query text. Do not execute SQL, create a saved record or change result state while building completion suggestions.

The read-only metadata may include optional distinct non-null values for the actual Header Status column. When the user types a single-quoted equality prefix on that declared column, offer the matching value, insert the correctly escaped value without a duplicate closing quote, and do not execute SQL or create a saved record. Completion remains read-only and uses query_schema metadata.

Use the DuckDB dialect of @dlh.io/dlh-sql-formatter version 1.3.0 for the explicit Format action in standalone and native Workbench surfaces. Apply two-space indentation, leading commas, lowercase clauses and a newline before the semicolon through a small token-aware adapter using the existing CodeMirror SQL parser. Uppercase SELECT keywords and keep FROM and WHERE with their following expression when no comment separates them. Preserve expressions, identifiers, strings, comments, CTEs and nested queries. Do not implement another parser or formatter. Apply the formatter through the normal editor-change path; formatting twice is stable when the input is accepted. If formatting fails, expose the error and leave the editor input and existing results unchanged. Native execution verification of this same contract remains a future acceptance check; status: not run.
