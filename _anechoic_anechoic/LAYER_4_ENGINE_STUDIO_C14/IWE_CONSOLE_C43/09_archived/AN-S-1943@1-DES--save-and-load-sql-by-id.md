---
atom_family: SPEC
atom_id: AN-S-1943
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-04 23:19:17 +0400
---

## Summary

Save and load SQL by ID

## Claim scope

Workbench SQL saved-query operations and saved-query references in Run, Check and the web URL.

## Claim

The Workbench **must**:

- save the selected SQL as an immutable UTF-8 `q_<uuid hex>.sql` file and a full Worksheet as `{"sql": "..."}` in an immutable `w_<uuid hex>.json` file under `.anechoic_runtime/workbench/saved_queries/`;
- return `saved_query_id`, `saved_query_url`, `kind` and `sql` from explicit query save, Worksheet save, Run and Check operations;
- expose `query_save({sql, cursor_position?}) -> {saved_query_id, saved_query_url, kind, sql}` and `worksheet_save({sql}) -> {saved_query_id, saved_query_url, kind, sql}`;
- expose `query_load({reference}) -> {saved_query_id, saved_query_url, kind, sql}` and `query_saved_list({limit?})` for recent query and Worksheet entries, with default limit 20 and maximum 1,000;
- expose the same contracts through the web `/save`, `/worksheet-save`, `/load` and `/saved-list` endpoints, and expose `query_schema({})` through `/schema` for table and column metadata;
- load a saved query or Worksheet by ID or URL and return its exact SQL without executing it;
- save the active statement before executing Run or Check and include its saved identity and exact SQL in success and query-error answers;
- return an explicit save error and not execute the query when saving fails;
- let `?query=<saved_query_id>` load either kind without automatic execution and preserve the `project_root` parameter;
- keep saved-query identities separate from materialized result query IDs and distinguish them with `kind`;
- omit sharing, authentication, deduplication, retry, repair, rollback, expiry and deletion workflows.
