---
atom_family: SPEC
atom_id: AN-S-2535
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: active
  version: 22
  updated_at: "2026-11-27T16:29:34.309627+00:00"
---
## Summary

Preserve governed Atom data and reuse native SQL.

## Claim scope

Direct file reading and native query semantics for Current, Draft, Backlog and explicitly loaded Archived Atom carriers.

## Claim

### Prose Claim

Discover Current and Draft Atom carriers throughout the selected Project’s `.anechoic_<project name>` authority root, independent of membership in the Current Scope Unit tree. Do not restrict Atom discovery to declared Scope directories or select a hard-coded Core path. Identify an Atom by its filename: `<configured Project prefix>-<one Role letter>-*.md`, with the prefix matched literally and the Role letter uppercase. YAML/Header markers and role-folder membership do not establish Atom identity. A matching file with invalid data is reported and excluded; folder/name/Header inconsistencies remain visible through the carrier audits when its data is readable. Keep each readable physical carrier as a separate row keyed by relative path and filename. Report duplicate Atom ID and Version across Current and loaded Archived carriers. Keep Drafts out of that duplicate audit. Select the first eligible declaration separately for model compilation. Current and numbered Draft references stay distinct, while role-only Draft technical references remain path-specific. Exclude derived Projections. Load Archived carriers only for requested Scope Unit and Role pairs. Read the admitted carriers into the derived DuckDB database; every Current status, including Done and Canceled, remains included. Parse YAML and actual CommonMark headings with the existing safe reader. Reuse the compiled Current-Declaration Content model, including Role and Form applicability, to generate Content schema and parse queryable CAPRMEDO Content. Expose only explicitly declared Content property paths, including inherited declarations, without a fixed Claim-heading list. Wildcards and bracketed formats, conditions or constraints restrict those declared properties; neither they nor observed Markdown headings declare new paths. Do not turn unrelated prose headings into Content properties or relabel non-RMEDO bodies as Claims. Compile schema only from supported Formal Claim declarations. Use the selected SQL engine’s semantics and native tokenization, without another SQL parser or evaluator.

Preserve raw Header properties, original Markdown and real heading paths privately without a fixed heading list or Form validation. Build flattened SQL columns for model-declared Header paths in Mode 1, observed raw Header paths in Mode 2, and model-admitted Content paths in both modes; source carriers, intermediate files and a third public source table are not created. Only Current Scope Unit Declarations establish current Scope Unit inventory; a Draft Declaration remains queryable only.

Use the Active Model for Relation names and derivation. Apply AN-S-3175 to Atom Relations. Each object row carries outgoing direct and declared-derived Relations; source or relevant Declaration changes refresh affected source/counterpart rows, mappings and hashes without source edits or Version changes. Use DuckDB and DuckPGQ for SQL/PGQ, pattern matching and traversal rather than a ANECHOIC traversal engine. Apply AN-S-1350 for typed reachability. Query each materialized inverse once.

Use native DuckDB for runtime lookups. Reuse existing tables and remove duplicate custom lookup indexes when their callers can query SQL. Archive bodies load on demand.

Normalize inverse writing from admitted legacy carriers using CA-M-509. Diagnose ambiguous aliases and unsupported derivations. Omit the affected projected facts. Keep timezone-aware values until the shared encoder returns ISO strings; retain required `pytz` rather than changing source-column casts.
