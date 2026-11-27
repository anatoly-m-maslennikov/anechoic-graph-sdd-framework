---
atom_family: SPEC
atom_id: AN-S-1229
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 12
  updated_at: "2026-11-26T19:17:02.414089+00:00"
---
# Summary

Define Implementation

## Claim

Implementation realizes RMED and can be edited directly. Its executable and non-executable parts are organized through its root Package.

### Formal claim

```text
Implementation > Package
```

## Semantics

Implementation is not a Projection. The root Package organizes its Modules, Prompts, Assets and nested Packages. Existing Documentation and Resources placements are retained in the review tree; this change does not equate logical parts with their Carriers. Each Implementation has one root Package.

## Details

Latest decisions: CA-A-1254 and CA-A-1255. Review Draft only; Current predecessor remains unchanged.

## Superseded — do not promote

CA-A-1259 removes Implementation as a primary kind. Its useful realization, direct-editing and Carrier/Runtime distinctions are retained in the Project Implementation Definition Draft. This older wrapper Draft is history only; Current R2173 remains unchanged pending the migration retirement pass.
