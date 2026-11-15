---
atom_id: CA-D-480
ref_id: CA-D-480
container:
  scope_unit: CA-SU-11
role: Delivery
form: Decision
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom
  dependencies:
  - CAPRMEDIO_MODEL <+ Atom.Content.Summary
  - CAPRMEDIO_MODEL <+ Atom.Header.Identity.ID
  - CAPRMEDIO_MODEL <+ Atom.Header.State.Status
  - CAPRMEDIO_MODEL <+ Carrier/File
tier: 3
status: Active
version: 25
updated_at: '2026-11-11 17:36:30 +0400'
carrier_destination:
  file:
    name: CA-D-480-CORE_META_MODEL-ENG_DECISION--keep-atom-addresses-consistent-with-carried-properties.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery/CA-D-480-CORE_META_MODEL-ENG_DECISION--keep-atom-addresses-consistent-with-carried-properties.md
  source_atom_id: CA-D-480
  source_atom_revision: 25
  source_sha256: 06b90a4625673e3745f14dc871f37eccad5a0c057738318199c6df7ac57c4d67
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Keep Atom addresses consistent with carried Properties

## Claim

### Prose Claim


Atom Properties represented by a filename, matching directory name, or placement.


**every** Atom Property represented by a filename, matching directory name, **or** placement **must** agree with its canonical internal value under the applicable Delivery encoding.

- compare resolved values using the registered encoding; a Summary Slug is checked against its Summary serialization, **not** against identical raw text.
- a mismatch is invalid **and** **must** be reported; the address **must not** silently override the value carried inside the Atom.
- agreement checking does **not** authorize rewriting the Atom **or** address. corrections require the applicable authorized change.

When an authorized parent Directory Carrier move carries a Current descendant, store the descendant's calculated `Header.Destination.File.Name` and `.Path` for the resulting location. For a descendant carried with its existing terminal Status, preserve its Status, Version, Updated At and Content. Treat the destination-only rewrite as a physical placement update within the existing Version.
