---
atom_id: CA-R-1432
ref_id: CA-R-1432
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Atom
  dependencies:
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_MODEL <+ Atom.Content.Summary
  - ANECHOIC_MODEL <+ Carrier
  - ANECHOIC_MODEL <+ Atom.Header.Context.Role
tier: 2
status: Active
version: 30
updated_at: 2026-11-04 18:34:50 +0400
carrier_destination:
  file:
    name: CA-R-1432-CORE_META_MODEL-RULE--govern-atom-lifecycle-identity-and-version.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1432-CORE_META_MODEL-RULE--govern-atom-lifecycle-identity-and-version.md
  source_atom_id: CA-R-1432
  source_atom_revision: 30
  source_sha256: d9b875a9b76593eb98d46d85fa02a703212d3f99696fde34fe72b286e87eaa69
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Govern Atom lifecycle identity and Version

## Claim

### Prose Claim

Draft edits and directly authorized in-place edits preserve the Atom's ID, Version, and Updated At. A Status-only change or archival preserves Version and Updated At; archival preserves the predecessor's unrelated content and uses the Archived Status and version-qualified identity.

Creating a Draft for a new Version of an existing Atom assigns Version N+1 once and initializes its creation timestamp. Promotion retains that planned Version and timestamp when Summary and Content Role are unchanged. A changed Summary or Content Role instead requires a fresh Atom ID and Version 1 at promotion. Lossless serialization that preserves the Summary value is not a Summary change.

A Current Atom update composes creation of a new Draft, archival of its Current predecessor, and promotion of the Draft. Capture the predecessor's Current Status once and use that same Status for promotion. A new Atom is assigned its own ID and initial Version. Moving an ancestor without changing a descendant's own bytes, metadata, direct owner, or placement relative to that owner does not edit that descendant.
