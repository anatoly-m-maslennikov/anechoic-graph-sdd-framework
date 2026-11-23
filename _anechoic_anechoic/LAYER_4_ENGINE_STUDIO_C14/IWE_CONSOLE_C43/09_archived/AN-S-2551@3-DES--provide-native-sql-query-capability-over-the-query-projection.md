---
atom_family: SPEC
atom_id: AN-S-2551
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-04 23:19:17 +0400
---
## Summary

Provide native SQL query capability over the query Projection

## Claim scope

Queries over the synchronized Atom query Projection.

## Claim

### Prose Claim

The query capability **must**:

- keep public queries read-only; they do not change source files or the query Projection.
- execute each public query synchronously and return its result or error to its originating MCP or web request. A query may contain multiple statements; Run and Check execute the statement selected by the optional cursor position, with a cursor exactly on a semicolon selecting the statement to its left, while Worksheet save preserves the whole script.
- accept native SQL according to the selected SQL engine's semantics.
- expose the parsed Header and mapped Content Properties without flattening their source distinctions.
- provide a read-only `query_schema({})` operation returning `{tables: {atoms: [{name, type}], scope_units: [{name, type}]}}`; `tables.atoms` includes declared `content.*` columns so the editor can autocomplete actual tables and quoted column names. This metadata operation does not read or write saved SQL files.
- provide `query_save({sql, cursor_position?})`, `worksheet_save({sql})`, `query_load({reference})` and `query_saved_list({limit?})`. `query_save` saves the selected statement; `worksheet_save` saves the whole script as a JSON object containing `sql`; `query_load` accepts an ID or URL; and `query_saved_list` returns recent query and Worksheet entries with `saved_query_id`, `saved_query_url`, `kind`, `preview` and `saved_at`. The default list limit is 20 and the maximum is 1,000.
- use the selected SQL engine for SQL semantics and its native tokenization for statement boundaries rather than introduce another SQL-like parser or evaluator.
- return a query error for invalid SQL; it **must not** return an empty successful result instead.
- keep source-file errors distinct from SQL errors.
