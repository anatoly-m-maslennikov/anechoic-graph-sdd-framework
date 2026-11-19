---
atom_id: CA-R-1280
ref_id: CA-R-1280
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Atom.Header.Context.Topics.Dependencies
  dependencies:
  - ANECHOIC_MODEL <+ Entity
  - ANECHOIC_MODEL <+ Atom.Header.Context.Topics
  - ANECHOIC_MODEL <+ Atom.Content
  - ANECHOIC_MODEL <+ Atom.Content.Summary
tier: 1
status: active
version: 35
updated_at: '2026-11-13T18:39:50.375078+00:00'
carrier_destination:
  file:
    name: CA-R-1280-CORE_META_MODEL-RULE--reference-every-prerequisite-subject-through-depends-on.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1280-CORE_META_MODEL-RULE--reference-every-prerequisite-subject-through-depends-on.md
  source_atom_id: CA-R-1280
  source_atom_revision: 35
  source_sha256: e2b18c299a8ee7c920a44bf6394fe131346478249f834deb58c927f886c26aa5
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Reference Every Prerequisite Subject through DEPENDS_ON

## Claim

### Prose Claim


coverage of canonical Subject Target mentions by an Atom's Subjects.


an Atom's Subjects, **when** present, **must** be exactly the distinct canonical Subject Targets independently mentioned **in** its Markdown Main Content, **not** an Atom citation label rendered under `CA-M-1024-CORE_META_MODEL-IMPLEMENTATION_METHOD--make-atom-claims-clear-and-preserve-their-meaning` as the referenced Atom's complete filename **without** its `.md` extension **or** directory path: zero **or** one GOVERNS target for its Claim, **and** DEPENDS_ON targets for **every** other mentioned Subject Target.

## Details

coverage includes Summary **and** **all** other body sections, nested headings, tables, examples, **and** reference labels. an Atom citation label is readable authority evidence, **not** a Subject Target mention **or** Subject target. this exclusion holds **when** the label occurs **in** the same sentence as Subject Target language; inventory that Subject Target **only** **when** the surrounding prose independently uses it. a mention outside Claim is **not** otherwise optional coverage. do **not** repeat GOVERNS **in** DEPENDS_ON **or** include a Subject Target absent from Main Content. a qualified Subject Path identifies its complete target; its component Terms and implicit bearer prefixes are **not** additional Subject Target mentions **unless** independently referenced. Subjects remain Relations rather than their targets. unresolved Subject Target mentions require resolution **before** coverage can pass.
