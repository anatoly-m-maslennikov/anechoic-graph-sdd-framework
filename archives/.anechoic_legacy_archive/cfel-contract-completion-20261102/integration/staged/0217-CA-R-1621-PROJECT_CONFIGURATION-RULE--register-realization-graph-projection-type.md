---
atom_id: CA-R-1621
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
status: Active
subjects:
  active: Projection/(.Form:=Realization Graph)
  passive:
  - Projection/(.Form:=Realization Graph)
  - Scope Unit//PROJECT_CONFIGURATION
  - Projection
  - Entity/Object/Continuant/Selection
  - ANECHOIC_MODEL <+ Projection
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Framework
    Settings
version: 19
updated_at: 2026-11-02 07:49:21 +0400
tier: 3
role: Requirement
form: Rule
context:
  topics:
    dependencies:
    - Projection/(.Form:=Realization Graph)
    - Scope Unit//PROJECT_CONFIGURATION
    - Projection
    - Entity/Object/Continuant/Selection
    - ANECHOIC_MODEL <+ Projection
    - ANECHOIC_MODEL <+ Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Framework
      Settings
---
## Summary

Register Realization Graph Projection Type

## Claim scope

the anechoic Project Configuration registration of the `realization_graph` Projection Type.

## Claim

the anechoic Project Configuration **must** register `realization_graph` as a specialized non-authoritative Projection Type for understanding existing Implementation **and** supporting reverse engineering into proposed RMED.

## Details

- registration uses the accepted specialized graph specification **and** the general Projection guarantees of CORE_META_MODEL; it does **not** add this Type **to** the universal Core requirements of other Projects.
- registration **and** activation remain distinct. the configured activation follows CA-R-1631; accepting this registration does **not** activate the Projection.
- the output remains a Projection under CA-R-2535. its permitted Implementation contribution under CA-R-1568 is **not** an Atom Content Role assigned **to** the Projection.
