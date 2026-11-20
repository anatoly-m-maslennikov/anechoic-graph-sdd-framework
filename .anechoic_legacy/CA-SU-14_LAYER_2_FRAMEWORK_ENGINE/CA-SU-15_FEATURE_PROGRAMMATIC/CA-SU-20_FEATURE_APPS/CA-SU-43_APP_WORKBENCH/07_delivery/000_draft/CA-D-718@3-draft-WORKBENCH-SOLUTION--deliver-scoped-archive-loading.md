---
identity:
  atom_id: CA-D-718
  ref_id: CA-D-718@3-draft
context:
  role: delivery
  form: solution
  tier: 5
  container:
    scope_unit: CA-SU-43
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development
      <+ Architecture <+ Communication <+ Interface Contracts
    dependencies:
    - MODEL//ANECHOIC <+ Projection
relations:
  delivery_for:
  - CA-R-2723
  - CA-M-465
  IS_REPLACEMENT_FOR:
  - CA-D-718
state:
  version: 3
  status: draft
  updated_at: '2026-11-14T07:53:03.724966+00:00'
destination:
  file:
    name: CA-D-718@3-draft-WORKBENCH-SOLUTION--deliver-scoped-archive-loading.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/07_delivery/000_draft
---
## Summary

Deliver scoped Archive loading

## Claim

### Prose Claim

Load selected Archives through MCP `workbench_archive_load` and HTTP
`POST /anechoic/{project}/api/archive-load`.

## Details

- Accept a nonempty `scopes` array of `{scope_unit, role}` pairs.
- Use the selected Project's shared owner. Keep the legacy URL as an alias.
- Complete when selected `atoms` rows are queryable. Audits may follow.
- Return the owner's full `loaded_archive_scopes` list, also shown by status.
