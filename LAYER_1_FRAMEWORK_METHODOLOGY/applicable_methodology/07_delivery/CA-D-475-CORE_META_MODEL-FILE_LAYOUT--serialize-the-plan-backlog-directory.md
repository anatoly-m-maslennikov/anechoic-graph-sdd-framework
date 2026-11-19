---
atom_id: CA-D-475
ref_id: CA-D-475
container:
  scope_unit: CA-SU-11
role: Delivery
form: file_layout
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan).Header.State.Status
    >| Status Group := Backlog
  dependencies:
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan)
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan).Header.Context.Label
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan).Header.State.Status
  - ANECHOIC_MODEL <+ Carrier/Directory
tier: 3
status: active
version: 29
updated_at: '2026-11-12T19:34:44.489998+00:00'
carrier_destination:
  file:
    name: CA-D-475-CORE_META_MODEL-FILE_LAYOUT--serialize-the-plan-backlog-directory.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery/CA-D-475-CORE_META_MODEL-FILE_LAYOUT--serialize-the-plan-backlog-directory.md
  source_atom_id: CA-D-475
  source_atom_revision: 29
  source_sha256: 799434458907741873897b930088ff7982d4066a8ea18219d290b3dfd67d53b7
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Serialize the Plan Backlog directory

## Claim

### Prose Claim

The Plan Backlog directory is `<owning scope unit>/<Plan Role folder>/<status folder>/`. It is a shared placement folder.

- Place a Backlog Plan directly in that folder when its direct Container is a Scope Unit or a Plan outside the Backlog group.
- When the direct Container is a Backlog Plan, place the file in that Plan's matching directory. Apply the same rule recursively.
- A Backlog Plan with contained Plans retains its matching directory and applicable descendant layout. Version labels use the ordinary Plan filename rule.
- Preserve the logical Container when placement uses the shared folder. Resolve containment from the Atom's Container.

The Formal Claim supplies the shared base directory. The direct Backlog Container rule supplies the more specific containing directory.

### Formal Claim

```python
placement_rules = ({"kind": "status", "role": "plan", "status": "backlog", "base": "role", "folder": "<status folder>"},)
```
