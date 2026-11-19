---
identity:
  atom_id: CA-R-3166
  ref_id: CA-R-3166@1-draft
context:
  role: Requirement
  form: Scope Delegation
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//WORKBENCH_FRONTEND
    dependencies:
    - ANECHOIC_STRUCTURE
  tier: 3
  container:
    scope_unit: CA-SU-43
state:
  status: draft
  version: 1
  updated_at: '2026-11-13T20:54:37.043605+00:00'
destination:
  file:
    name: CA-R-3166@1-draft-WORKBENCH-SCOPE_DELEGATION--delegate-workbench-frontend-responsibilities-and-local-admissions.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/04_requirement/000_draft
author: Anatoly Maslennikov
relations:
  IS_REPLACEMENT_FOR:
  - CA-R-2764
---
## Summary

Delegate WORKBENCH_FRONTEND responsibilities and local admissions

## Claim

### Prose Claim

WORKBENCH_FRONTEND owns the Workbench query UI, component palette, presentation, formatting, page navigation and frontend state. Shared Workbench requirements and cross-interface contracts remain in WORKBENCH.

The receiving Scope Unit is WORKBENCH_FRONTEND. The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `MODEL//ANECHOIC <+ Projection`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Packaging`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Component Structure`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Code Authoring`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Query Authoring <+ SQL`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspect//Visual Design`;

- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Libraries and Frameworks`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Component Authoring`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Code Style`;
