---
atom_family: SPEC
atom_id: AN-S-2535
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 10
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary

Preserve governed Atom data and reuse native SQL.

## Claim scope

Direct file reading and native query semantics for Current and Draft Atom carriers excluding Archived carriers.

## Claim

### Prose Claim

The DuckDB Projection reader must read Current and Draft Atom carriers, excluding Archived carriers, into the derived DuckDB database. Every Current status, including Done and Canceled, remains in that inventory. Parse YAML and Markdown directly using the existing safe YAML reader and CommonMark headings. Generate the Content schema from Current model Declarations. Compile declared Content paths and their applicability; do not evaluate arbitrary CFEL formulas or interpret prose as schema.

Preserve all parsed raw Header properties, the original Markdown body, and real heading paths without a fixed heading list or Form validation. Parent paths are derived from Property path segments. The reader creates no intermediate source-data files or third public source table. Its schema is a rebuildable derived asset under `.anechoic_runtime/workbench`, with one flattened SQL column for every observed raw Header Property path and Content columns from model-declared Properties.

Only Current Scope Unit Declarations establish the current Scope Unit inventory. A Draft Declaration remains a queryable Atom but does not establish a current Scope Unit.

Source carriers remain unchanged. Normalize admitted authored inverse writing before materializing canonical direct facts. Each indexed object row carries that object's outgoing direct and declared-derived Relations. For `Task IS_CONTAINED_BY Epic`, the Task row carries `IS_CONTAINED_BY` and the Epic row carries the derived `CONTAINS`. A source or relevant Declaration change refreshes every affected outgoing-relation row, graph mapping, and row hash, including rows for unchanged target sources. This does not edit those sources or increment their Versions. Each public row hash includes its materialized Relations.

Use DuckDB for SQL and the DuckPGQ community extension for SQL/PGQ graph queries. Register a property graph over the indexed objects and their materialized registered Relation facts. Reuse DuckPGQ for pattern matching and traversal instead of implementing a ANECHOIC traversal engine or requiring a custom `expand()` API.

Reachability queries must still satisfy the Relation-expansion requirement: resolve an unambiguous typed seed, follow the selected Relation Types and directions, include the seed and each reachable typed reference once, and terminate on cycles. Use native SQL and SQL/PGQ to produce that result; joins or subqueries fetch the selected objects. Querying a declared inverse uses its materialized fact and does not synthesize it again. The Projection does not add a SQL-like parser, evaluate Formal Claims, or adopt graph algorithms beyond the selected query requirements.

Use the canonical Relation registry under CA-M-509 for Relation-name resolution and direct/derived materialization. Compile applicable Current Requirement relation Declarations, including Relation Declaration, using explicit inverse aliases and literal unqualified inverse bindings. An explicit inverse alias needs no separate Relation Declaration. Normalize authored inverse writing through its unambiguous declared canonical counterpart, swapping endpoints once and preserving the same fact without editing its source. Build each inverse view once from the canonical direct fact. Direct graph facts come from authored Header Relations and declared Scope Unit/Atom ownership references. Do not evaluate arbitrary prose, general CFEL formulas or qualified Model derivation rules.

Include `pytz`, required by DuckDB for fetching timezone-aware timestamps into Python. Keep those values timezone-aware until the shared result encoder returns ISO strings; do not cast source columns to work around a missing runtime dependency.
