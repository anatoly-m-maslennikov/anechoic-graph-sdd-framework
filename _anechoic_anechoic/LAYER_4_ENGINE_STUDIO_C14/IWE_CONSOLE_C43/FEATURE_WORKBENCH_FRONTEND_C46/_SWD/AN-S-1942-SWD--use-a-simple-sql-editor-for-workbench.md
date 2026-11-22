---
atom_family: SPEC
atom_id: AN-S-1942
container:
  component: C46
tier: 4
context:
  lens: SWD
state:
  status: active
  version: 8
  updated_at: '2026-11-12T12:34:26.975035+00:00'
---
## Summary

Use a simple SQL editor for Workbench

## Claim scope

Workbench SQL editing, schema completion and query actions.

## Claim

### Prose Claim

Use CodeMirror 6 SQL support and read-only `query_schema({})` metadata: `atoms` name/type/optional values, `scope_units` name/type, and technical `change_log` only `observed_at`, `operation`, `old_path`, `new_path`. Complete actual tables, declared dotted snake_case `content.*` columns and quoted identifiers as needed; do not read saved SQL for suggestions or expose space-based Content names.

Each Tab holds one query. Preserve quotes, comments and CTEs and distinguish delimiters inside them. Send the complete query for Run or Check under CA-R-2728. CodeMirror supplies editing, highlighting and completion. Cmd+Enter runs and Shift+Cmd+Enter checks; Run & Save follows successful Run and Save snapshots complete text. Completion never executes SQL, saves or changes results. On a single-quoted equality prefix for actual Header Status, offer metadata value with correct escaping/closing quote.

Format uses DuckDB dialect `@dlh.io/dlh-sql-formatter` 1.3.0 through a small token-aware adapter and existing CodeMirror parser: two-space indent, leading commas, uppercase SELECT, lowercase clauses, newline before semicolon, with FROM/WHERE attached to following expression absent a separating comment. Preserve expressions/identifiers/strings/comments/CTEs/nesting. Apply normal editor change path; accepted formatting is idempotent. On failure show error and preserve editor/results. Do not add a parser/formatter/backend capability; native execution verification remains future, not run.
