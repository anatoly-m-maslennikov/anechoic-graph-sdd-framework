---
identity:
  atom_id: CA-M-500
  ref_id: CA-M-500@15
context:
  container:
    scope_unit: CA-SU-45
  role: Method
  form: Decision
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Schema
    dependencies:
    - MODEL//CAPRMEDIO <+ Projection
  tier: 4
relations:
  method_for:
  - CA-R-2726
  IS_REPLACEMENT_FOR:
  - CA-M-500
state:
  status: archived
  version: 15
  updated_at: '2026-11-13T21:05:56.059500+00:00'
destination:
  file:
    name: CA-M-500@15-WORKBENCH_BACKEND-DECISION--rebuild-the-workbench-schema-from-source-atoms.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/05_method/099_archived
author: Anatoly Maslennikov
---
## Summary

Rebuild the Workbench schema from source Atoms.

## Claim scope

The schema asset and source tables used by WORKBENCH_BACKEND.

## Claim

### Prose Claim

Use a rebuildable schema asset. Use the same dotted snake_case paths in the asset, SQL, MCP results, and `query_schema` (for example, `header.identity.atom_id` and `content.claim.formal_claim`).

#### Build and startup

- Refresh mode uses the Current Declarations selected by CA-M-1011, including its first-refresh bootstrap. Generate and validate `workbench_schema.json`. Existing mode uses the checkout asset.
- Load the asset at startup. Report a missing or invalid asset. Apply Declaration changes by refreshing the asset and rebuilding the image. Ordinary data changes and rereads use the loaded schema.

#### Header

- Mode 1 uses Current Declarations and the grouped Header adapter. Bind `Header.ID` to `identity.atom_id`. Use aliases only for reads and reject conflicts. Keep offset-bearing timestamps as `TIMESTAMPTZ`.
- Mode 2 is enabled. At cold start, include all observed Header paths from valid files, including empty paths and distinct source spellings. Use JSON for `header.context.container` (the only grouping-node exception) and for `header.relations` (direct and derived).
- Both modes preserve source Headers and use the Current-model parser without adding a full Form validator.

#### Content

- Workbench can query Content for all Roles. Current Declarations determine which sections are queryable.
- Parse actual Markdown heading paths. Preserve complete mapped Content and keep empty declared columns. Use each Role’s declared sections.
- Apply Role and Form rules, inheritance, wildcards, and more specific rules. Only explicit property declarations name columns. Resolve competing Declarations separately from selecting eligible inputs. Keep exact provenance.

#### Source files

- Parse complete YAML. Preserve missing, null, empty, scalar, list, map, false, and zero values in Header and Content.
- A Scope Unit’s Current Declaration defines its structure. The Project Scope Unit is predetermined. Folders and paths represent that structure.
- Index readable files separately, including Draft structural files. Report schema violations and duplicate revisions in the audit tables. Keep only the mapped data.

#### Model facts

- Read facts only from accepted code blocks in `Content.Claim.Formal Claim`. Ignore comments outside strings when identifying declarations and extracting facts. Prose Claim, Semantics, Details, examples, and Header Topics supply no facts.
- Use identity, lifecycle, and provenance metadata to select and bind inputs. Mode 2 Header observations supply data only.
