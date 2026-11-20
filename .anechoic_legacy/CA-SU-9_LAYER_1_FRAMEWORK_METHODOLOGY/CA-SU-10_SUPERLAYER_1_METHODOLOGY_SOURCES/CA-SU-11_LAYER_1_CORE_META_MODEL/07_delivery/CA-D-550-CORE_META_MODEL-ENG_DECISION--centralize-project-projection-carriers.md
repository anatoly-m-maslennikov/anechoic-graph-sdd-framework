---
atom_id: CA-D-550
ref_id: CA-D-550
container:
  scope_unit: CA-SU-11
role: Delivery
form: Decision
topics:
  main_subject: ANECHOIC_MODEL <+ Carrier/Directory
  dependencies:
  - ANECHOIC_MODEL <+ Project
  - ANECHOIC_MODEL <+ Projection
  - ANECHOIC_MODEL <+ Carrier
  - 'ANECHOIC_MODEL <+ Entity/Object/Continuant/Projection/Type: Applicable Methodology'
  - ANECHOIC_MODEL <+ Journal
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_MODEL <+ Scope Unit
  - ANECHOIC_MODEL <+ Project.Settings
tier: 3
status: Active
version: 20
updated_at: 2026-11-02 19:44:26 +0400
carrier_destination:
  file:
    name: CA-D-550-CORE_META_MODEL-DECISION--centralize-project-projection-carriers.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Centralize Project Projection Carriers

## Claim

### Prose Claim


persistent non-authoritative view Projection Carriers belonging to a Project.


**all** persistent view Projection Carriers of a Project **must** reside under **`=1`** Directory Carrier: `.anechoic_<project_name>/_projection/`, **except** Applicable Methodology, whose Carrier Root **must** remain `.anechoic_<project_name>/000_ANECHOIC_framework/00_APPLICABLE_METHODOLOGY/`.

## Details

- Graphs **and** derived Journal views use `_projection/` **or** named subdirectories beneath it.
- Applicable Methodology uses its separate Carrier Root; its Methodology Sources retain the `000_APPLICABLE_MTHD_sources/` subdirectory.
- Authoritative Atoms, Methodology Sources, Project Settings, and Project Structure retain their own authoritative locations.
- Temporary build stages **and** intermediate reports remain ephemeral; publication places the delivered view Projection under its declared Carrier Root.
- The derivation RMED → using O → I does not relocate native Implementation into _projection: native I uses its governed Delivery place and may supply actual-state source facts. Views subsequently generated from I use _projection.
