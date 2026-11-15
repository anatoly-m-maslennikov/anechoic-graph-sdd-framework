---
identity:
  id: CA-D-716
  ref_id: CA-D-716
context:
  container:
    scope_unit: CA-SU-11
  role: delivery
  form: file_layout
  topics:
    main_subject: CAPRMEDIO_MODEL <+ Atom.Header.State.Status >| Status Group := Draft
    dependencies:
    - CAPRMEDIO_MODEL <+ Carrier
  tier: 3
state:
  status: active
  version: 5
  updated_at: '2026-11-12T19:34:49.576334+00:00'
destination:
  file:
    name: CA-D-716-CORE_META_MODEL-FILE_LAYOUT--place-draft-atom-carriers-in-the-owning-role-folder.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery/CA-D-716-CORE_META_MODEL-FILE_LAYOUT--place-draft-atom-carriers-in-the-owning-role-folder.md
  source_atom_id: CA-D-716
  source_atom_revision: 5
  source_sha256: b4921d1a09508e4e5dc4ea91cb85be7d7c5a70333a12667eb8b925e9c06a5a7d
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Place Draft Atom Carriers in the owning Role folder

## Claim

### Prose Claim

Place Draft Atom Markdown Carriers in the shared `<owning scope unit>/<role folder>/<status folder>/` directory. The Atom's owning Scope Unit and Role determine this directory.

### Formal Claim

```python
placement_rules = ({"kind": "status", "role": None, "status": "draft", "base": "role", "folder": "<status folder>"},)
```
