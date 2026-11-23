---
atom_family: SPEC
atom_id: AN-S-4356
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: '2026-11-13T20:54:08.776407+00:00'
---
## Summary

Constrain public DuckDB queries to native read-only access

## Claim scope

Trusted public SQL and internal result materialization for one Project.

## Claim

### Prose Claim

Admit one whole trusted read query through MCP or the Workbench web interface using DuckDB native parsing and query APIs, including DuckPGQ SQL/PGQ. A Run or Check never selects a statement or fragment at a cursor. Use native tokenization when extraction cannot support the grammar. Add no SQL parser, function sandbox or second query language.

Execute the accepted SELECT-only query once into a DuckDB-owned generated result table in a normal native transaction. Public input cannot submit DDL/DML; the trusted cache write may COMMIT. Retain ordered native column metadata, including duplicates, and deliver bounded pages from that stable result. Preview uses native `relation.limit(N)` without rewriting submitted SQL, preserves an existing SQL LIMIT, supports CTE/GRAPH_TABLE, and changes counts to the capped execution; absent preview adds no cap.

Keep exact submitted SQL (comments, Unicode and LIMIT) internal. Ordinary Run, Check and Page responses never echo it. Save appends the Bookmark only after materialization; a save failure returns the completed result ID/metadata with `outcome: partial` and `save_error`, without retry or rollback. Failed queries create no saved entry; unsaved Run, Check and Page have no Journal effect. Page transforms use only the existing result table and never rerun, parse, append to or rewrite SQL. At materialization, use one native cache with a private quoted ordinal before public columns; apply preview before snapshot numbering. Resolve public indices to physical positions, never user names or DuckDB `rowid`. Use the ordinal as the final stable page tie-breaker, never as public metadata or a filter/group value. Bind literal filter values with native DuckDB, use `NULLS LAST`, put group order before sort, and calculate window counts before offset/limit. Do not add a second cache, ALTER, UPDATE, rescan, raw SQL grid clause, endpoint or service.

The dedicated result lifecycle owns retention, View pinning, restart disposal and runtime-setting reads. Startup loads bundled DuckPGQ before disabling external access, autoinstall/autoload and public configuration changes; database/spill writes stay in the owned runtime directory and sources stay unchanged. Reject/unknown/storage/delivery errors return useful caller reasons and stderr diagnostics. Invalid requests are recoverable `query_error` WARNING failures; unavailable/unexpected owner failures are ERROR/blocked with the existing restart or generic boundary. DuckPGQ management calls may invalidate the connection; this trusted-input MVP promises no capability sandbox, retry, restoration or connection recovery.

## Details

### Proposal

**Provisional rewrite.**

Should this Method keep the public response and Bookmark rules, or refer to the Atoms that own those rules?

Proposed answer: keep native parsing, materialization, the stable page ordinal and DuckDB limits here. Use CA-R-2728@10 for the public read-only boundary, CA-D-673@20 and CA-D-724@1 for delivery, and CA-O-240@13-draft for the Run and Check sequence. Keep any conditions that only this Method states.

Effect: the Method gets shorter. Public responses and Action behavior stay the same. The Claim retains the source wording for the passages in question until the allocation is confirmed.
