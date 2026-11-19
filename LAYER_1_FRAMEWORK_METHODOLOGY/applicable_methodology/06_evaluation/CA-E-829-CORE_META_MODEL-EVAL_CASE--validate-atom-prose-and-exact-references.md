---
identity:
  atom_id: CA-E-829
  ref_id: CA-E-829
context:
  role: evaluation
  form: Eval Case
  tier: 4
  topics:
    main_subject: ANECHOIC_MODEL <+ Term
    dependencies:
    - ANECHOIC_MODEL <+ Atom
    - ANECHOIC_MODEL <+ Atom.Content
    - ANECHOIC_MODEL <+ Scope Unit.Name
    - ANECHOIC_MODEL <+ Carrier/File
  container:
    scope_unit: CA-SU-11
relations:
  evaluation_for:
  - CA-M-1014
  - CA-M-1021
  - CA-M-1022
state:
  version: 1
  status: active
  updated_at: '2026-11-13T18:15:43.503236+00:00'
destination:
  file:
    name: CA-E-829-CORE_META_MODEL-EVAL_CASE--validate-atom-prose-and-exact-references.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/06_evaluation
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/06_evaluation/CA-E-829-CORE_META_MODEL-EVAL_CASE--validate-atom-prose-and-exact-references.md
  source_atom_id: CA-E-829
  source_atom_revision: 1
  source_sha256: 116126bb3f43c94b6b3c96aabc54b9721680e1031627d2770eb0a503aaedbb83
  original_relations_sha256: 7918e9348d6fb352077d65d85ab84fa4f8598f0650a1a8ebd7430243fe54132e
---
## Summary

Validate Atom prose and exact references

## Claim

### Prose Claim

Evaluate authored Atom prose against the applicable ASD-STE100-aligned profile. Check exact canonical Terms, Scope Unit Names, registered references, and literal identifiers against their authoritative sources.

Use fixtures with ordinary sentence and list starts, correct exact names and references in both positions, altered exact names or references, mismatched Term meanings, and literal Python, SQL, Topic, and Relation tokens that must remain unchanged. Identify the exact profile and authority revisions and expected results.

Report each affected occurrence, its observed and expected form, and the authority. Treat ambiguous or unavailable evidence as unresolved. Record a Concern and do not rewrite the source.
