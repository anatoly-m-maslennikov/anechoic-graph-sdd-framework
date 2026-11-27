---
atom_family: SPEC
atom_id: AN-S-1942
container:
  component: C46
tier: 4
context:
  lens: SWD
state:
  status: draft
  version: 9
  updated_at: '2026-11-13T20:50:51.490629+00:00'
---
## Summary

Use a simple SQL editor for Workbench

## Claim scope

Workbench SQL editing, schema completion and query actions.

## Claim

### Prose Claim

Use CodeMirror 6 SQL support and read-only `query_schema({})` metadata: name, type and optional values for `atoms`; name and type for `scope_units`; and only `observed_at`, `operation`, `old_path` and `new_path` for the technical `change_log`. Complete actual tables, declared dotted snake_case `content.*` columns and quoted identifiers as needed. Do not read saved SQL for suggestions or expose space-based Content names.

Each Tab holds one query. Preserve quotes, comments and CTEs, and distinguish delimiters inside them. Send the complete query for Run or Check under CA-R-2728. CodeMirror supplies editing, highlighting and completion. Cmd+Enter runs; Shift+Cmd+Enter checks. Run & Save follows successful Run; Save snapshots complete text. Completion never executes SQL, saves or changes results. On a single-quoted equality prefix for actual Header Status, offer the metadata value with correct escaping and closing quote.

Format uses DuckDB dialect `@dlh.io/dlh-sql-formatter` 1.3.0 through a small token-aware adapter and the existing CodeMirror parser. Use two-space indent, leading commas, uppercase SELECT, lowercase clauses and a newline before the semicolon. Attach FROM/WHERE to the following expression unless a comment separates them. Preserve expressions, identifiers, strings, comments, CTEs and nesting. Apply formatting through the normal editor change path; accepted formatting is idempotent. On failure show an error and preserve editor and results. Add no parser, formatter or backend capability. Native execution verification remains future, not run.
