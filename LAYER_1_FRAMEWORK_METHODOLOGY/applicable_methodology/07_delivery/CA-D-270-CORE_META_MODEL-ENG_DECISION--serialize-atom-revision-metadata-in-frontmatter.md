---
atom_id: CA-D-270
ref_id: CA-D-270
container:
  scope_unit: CA-SU-11
role: Delivery
form: Decision
topics:
  main_subject: ANECHOIC_MODEL <+ Atom
  dependencies:
  - ANECHOIC_MODEL <+ Atom.Header.State.Version
  - ANECHOIC_MODEL <+ Atom.Header.State.Updated At
tier: 3
status: Active
version: 27
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-D-270-CORE_META_MODEL-DECISION--serialize-atom-revision-metadata-in-frontmatter.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery/CA-D-270-CORE_META_MODEL-ENG_DECISION--serialize-atom-revision-metadata-in-frontmatter.md
  source_atom_id: CA-D-270
  source_atom_revision: 27
  source_sha256: b916d4feb0fdf7ef699ff37c089093a6add9ef25a16da15fed96b80b127b6c21
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Serialize Atom Revision Metadata **in** Frontmatter

## Claim

### Prose Claim


Markdown Atom Revision Carriers.


**every** Markdown Atom Revision Carrier **must** serialize its positive integer Version as `version` **and** its Project-time Updated At value as `updated_at` **in** YAML frontmatter.

## Details

- `version` is a YAML integer **>=1**, **not** a Boolean **or** numeric string.
- `updated_at` is a quoted YAML string containing **=1** valid date, time **and** explicit UTC offset. accept the existing `YYYY-MM-DD HH:MM:SS +HHMM` form **and** the equivalent ISO 8601 `YYYY-MM-DDTHH:MM:SSZ` **or** `YYYY-MM-DDTHH:MM:SS+HH:MM` form, including optional fractional seconds. offset signs **may** be positive **or** negative; reject a missing timezone, impossible date, **or** invalid offset.
- lexical differences representing the same instant do **not** alone change Revision identity. this Delivery serializes Updated At; it does not classify whether an edit changes governed meaning.
