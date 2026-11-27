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
  version: 16
  updated_at: 2026-11-11 05:02:55 +0400
---
## Summary

Preserve governed Atom data and reuse native SQL.

## Claim scope

Direct file reading and native query semantics for Current and Draft Atom carriers excluding Archived carriers.

## Claim

### Prose Claim

Discover Current and Draft Atom carriers throughout the selected Project’s `.anechoic_<project name>` authority root, independent of membership in the Current Scope Unit tree. Do not restrict Atom discovery to declared Scope directories or select a hard-coded Core path. Identify an Atom by its filename: `<configured Project prefix>-<one Role letter>-*.md`, with the prefix matched literally and the Role letter uppercase. YAML/Header markers and role-folder membership do not establish Atom identity. A matching file with invalid data is reported and excluded; folder/name/Header inconsistencies remain visible through the carrier audits when its data is readable. For duplicate Atom references, load the first encountered readable carrier and report each later duplicate in the existing query-visible Atom issue table; no ordering preference is required. Use the same selected carrier for query data and declaration compilation. Current and numbered Draft references stay distinct, while role-only Draft technical references remain path-specific. Apply the existing carrier, lifecycle and invalid-source checks; Archived carriers and derived Projections remain excluded. Read the admitted carriers into the derived DuckDB database; every Current status, including Done and Canceled, remains included. Parse YAML and actual CommonMark headings with the existing safe reader. Reuse the compiled Current-Declaration Content model, including Role and Form applicability, to generate Content schema and parse queryable CAPRMEDO Content. Expose only explicitly declared Content property paths, including inherited declarations, without a fixed Claim-heading list. Wildcards and bracketed formats, conditions or constraints restrict those declared properties; neither they nor observed Markdown headings declare new paths. Do not turn unrelated prose headings into Content properties or relabel non-RMEDO bodies as Claims. Do not evaluate arbitrary CFEL or prose as schema. Use the selected SQL engine’s semantics and native tokenization, without another SQL parser or evaluator.

Preserve raw Header properties, original Markdown and real heading paths privately without a fixed heading list or Form validation. Build flattened SQL columns for model-declared Header paths in Mode 1, observed raw Header paths in Mode 2, and model-admitted Content paths in both modes; source carriers, intermediate files and a third public source table are not created. Only Current Scope Unit Declarations establish current Scope Unit inventory; a Draft Declaration remains queryable only.

Normalize admitted authored inverse writing before materializing canonical direct facts. Each object row carries outgoing direct and declared-derived Relations; source or relevant Declaration changes refresh affected source/counterpart rows, mappings and hashes without source edits or Version changes. Use DuckDB and DuckPGQ for SQL/PGQ, pattern matching and traversal rather than a ANECHOIC traversal engine. Reachability resolves an unambiguous typed seed, selected relation types/directions, includes each typed reference once and terminates cycles; querying an inverse uses its materialized fact once.

Use CA-M-509's registry for relation names, exact inverse aliases and literal unqualified inverse bindings. Ambiguity is diagnosed and omitted, never guessed; qualified model derivations remain out of runtime facts. Keep timezone-aware values until the shared encoder returns ISO strings; retain required `pytz` rather than changing source-column casts.
