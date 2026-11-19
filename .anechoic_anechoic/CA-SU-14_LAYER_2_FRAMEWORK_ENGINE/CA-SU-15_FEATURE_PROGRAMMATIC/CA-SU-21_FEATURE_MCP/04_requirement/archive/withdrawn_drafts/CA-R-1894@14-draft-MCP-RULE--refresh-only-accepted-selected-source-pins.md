---
identity:
  atom_id: CA-R-1894
  ref_id: CA-R-1894@14-draft
context:
  container:
    scope_unit: CA-SU-21
  role: requirement
  form: rule
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Output Publication
    dependencies:
    - PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data
      Handling <+ Source Selection
    - MODEL//ANECHOIC <+ Projection
    - MODEL//ANECHOIC <+ Atom/(.Header.Role := Operations)/Workflow
    - MODEL//ANECHOIC <+ Atom/(.Header.Role := Operations)/Action
    - MODEL//ANECHOIC <+ Actor/Operator
    - MODEL//ANECHOIC <+ Journal
    - MODEL//ANECHOIC <+ Atom
    - MODEL//ANECHOIC <+ Carrier/File
  tier: 3
state:
  status: draft
  version: 14
  updated_at: 2026-11-10 03:34:41 +0400
destination:
  file:
    name: CA-R-1894@14-draft-MCP-RULE--refresh-only-accepted-selected-source-pins.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-21_FEATURE_MCP/04_requirement/draft
current_scope_unit: MCP
author: Anatoly Maslennikov
---
## Summary

Refresh only accepted selected source pins

## Claim scope

the exact admitted selected-source revision refresh under the current Epic.

## Claim

### Prose Claim

the selected binding Projection **must** support an explicitly authorized refresh of the exact source revision registered by CA-D-588-MCP-DELIVERY--register-the-prepared-successor-binding-refresh, while preserving its admitted capability identities and graph.

## Details

- the registered source revision is authority; the refreshed binding is derived evidence, not new authority.
- preserve **all** route identities, order, Steps, Actions, native calls, edges, query admissions and registry identity. **only** the registered version and digest occurrences and resulting derived digests change.
- retain exact current Operator authorization, source-currentness checks, publication intent, readback and Journal completion. a pending recording is not completed publication.
- unknown revisions, changes to topology or capability admission remain outside this refresh.

