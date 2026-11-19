---
atom_id: CA-D-654
ref_id: CA-D-654
container:
  scope_unit: CA-SU-11
role: Delivery
form: Policy
topics:
  main_subject: ANECHOIC_MODEL <+ Node/Occurrent
  dependencies:
  - ANECHOIC_MODEL <+ Carrier
  - ANECHOIC_MODEL <+ Event Record
  - ANECHOIC_MODEL <+ Relation//CARRIES
tier: 1
status: Active
version: 3
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-D-654-CORE_META_MODEL-POLICY--represent-occurrent-information-through-continuant-records.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery/CA-D-654-CORE_META_MODEL-POLICY--represent-occurrent-information-through-continuant-records.md
  source_atom_id: CA-D-654
  source_atom_revision: 3
  source_sha256: 770f6ed96abaf0abb954cbc154ec43537cd2bb6a1f7e3d93769541da4a66648c
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Represent Occurrent information through Continuant records

## Claim

### Prose Claim


representation of an Occurrent's recorded information.


An Occurrent is not carried or stored as the occurrence itself. When
information about an Occurrent is retained, a Continuant record represents
that information; the Carrier binds the Continuant record, not the Occurrent.
An Event Record in a Journal is one such record.

This reusable Policy governs Occurrent representation. It creates no new
Carrier, per-occurrence binding, Journal record, or relation type.

## Semantics

The Event remains the actual occurrence. Its Event Record is a distinct
Continuant that may have a Carrier. CARRIES and its derived IS_CARRIED_BY view
therefore apply to the represented non-ephemeral record rather than directly
to the Occurrent.

## Details

This Policy reuses CA-R-1958, CA-R-1968@12, CA-R-2590, and CA-R-1993. It fills
the missing reusable D Policy boundary without changing their definitions or
introducing a direct Occurrent-to-Carrier fact.
