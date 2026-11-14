---
identity:
  atom_id: CA-M-464
  ref_id: CA-M-464@20-draft
context:
  container:
    scope_unit: CA-SU-45
  role: Method
  form: Solution
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Source Retrieval
    dependencies:
    - MODEL//CAPRMEDIO <+ Projection
    - CAPRMEDIO_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling
      <+ Schema
  tier: 4
relations:
  method_for:
  - CA-R-2723
  - CA-R-2726
  - CA-R-2728
  - CA-R-2724
  IS_REPLACEMENT_FOR:
  - CA-M-464
state:
  status: draft
  version: 20
  updated_at: '2026-11-13T23:58:46.146921+00:00'
destination:
  file:
    name: CA-M-464@20-draft-WORKBENCH_BACKEND-SOLUTION--preserve-governed-atom-data-and-reuse-native-sql.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/05_method/000_draft
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Preserve governed Atom data and reuse native SQL.

## Claim

### Prose Claim

Use direct file reading and native SQL for Current, Draft, Backlog,
and explicitly loaded Archived Atom carriers.

## Details

### Carrier selection

- Discover Current and Draft carriers throughout the selected Project’s
  `.caprmedio_<project name>` authority root.
  - Scope Unit membership does not limit discovery. Use no hard-coded Core path.
- Match `<configured Project prefix>-<one Role letter>-*.md`.
  Match the prefix literally and the Role letter in uppercase.
  - YAML markers and Role folder membership do not establish Atom identity.
- Report and exclude a matching file with invalid data.
  Report folder, name, and Header inconsistencies for readable files in carrier audits.
- Key each readable carrier row by relative path and filename.
- Audit duplicate Atom ID and Version across Current and loaded Archived
  carriers. Exclude Drafts from that audit.
- Select the first eligible declaration separately for model compilation.
- Keep Current and numbered Draft references distinct.
  Keep role-only Draft technical references path-specific.
- Exclude derived Projections. Load Archive bodies only for requested
  Scope Unit and Role pairs.

### Source parsing

- Load admitted carriers into derived DuckDB. Include every Current status,
  including Done and Canceled.
- Use the existing safe reader for YAML and actual CommonMark headings.
  - Preserve raw Header, original Markdown, and real heading paths privately.
  - The private reader uses no fixed heading list or Form validation.
- Only Current Scope Unit Declarations establish the current inventory.
  Draft Declarations remain queryable.

### Schema

- Use the compiled Current-Declaration Content model for Content schema
  and parsing across CAPRMEDO, with Role and Form applicability.
- Expose only explicitly declared property paths, including inherited paths.
  - Wildcards and bracketed formats, conditions, and constraints restrict paths.
  - Those restrictions and observed Markdown headings declare no new paths.
  - Keep unrelated headings as prose. Use each Role’s declared Content sections.
- Compile schema only from supported Formal Claim declarations.
- Expose model-declared Header paths in Mode 1 and observed raw Header paths
  in Mode 2. Both modes expose model-admitted Content paths as SQL columns.
- Create no source carriers, intermediate files, or third public source table.

### Relations and traversal

- Normalize admitted authored inverses before materializing canonical direct facts.
- Use CA-M-509’s registry for names, exact inverse aliases, and literal
  unqualified inverse bindings.
  - Report and omit ambiguity. Keep qualified derivations out of runtime facts.
- Each row carries outgoing direct and declared-derived Relations.
  - Source or relevant Declaration changes refresh affected source and
    counterpart rows, mappings, and hashes without editing source or Versions.
- Use DuckDB and DuckPGQ for SQL/PGQ, pattern matching, and traversal.
  - Use the SQL engine’s own semantics and tokenization.
  - Use no extra parser, evaluator, or CAPRMEDIO traversal engine.
- Reachability resolves one unambiguous typed seed and the selected types
  and directions.
  - Include each typed reference once. Terminate cycles.
  - Use each materialized inverse fact once.

### Lookups and encoding

- Use native DuckDB for runtime lookups. Reuse existing tables.
  Remove duplicate custom indexes where their callers can query SQL.
- Keep timezone-aware values until the shared encoder returns ISO strings.
  Retain required `pytz` and existing source-column casts.

### Proposal

Provisional. Confirm when a relation Declaration change takes effect.
CA-M-464@19 mentions affected-row refresh. CA-M-509@9 uses a rebuild.
Preserve both until the refresh boundary is confirmed.
