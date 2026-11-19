---
identity:
  atom_id: CA-R-2792
  ref_id: CA-R-2792
context:
  container:
    scope_unit: CA-SU-11
  role: Requirement
  form: Declaration
  topics:
    main_subject: MODEL//ANECHOIC <+ (Workspace, Workspace.native_thread_id, Workspace.project_root)
  tier: 3
state:
  status: active
  version: 5
  updated_at: '2026-11-13T04:20:57.712025+00:00'
destination:
  file:
    name: CA-R-2792-CORE_META_MODEL-DECLARATION--define-workspace.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
author: Anatoly Maslennikov
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2792-CORE_META_MODEL-DECLARATION--define-workspace.md
  source_atom_id: CA-R-2792
  source_atom_revision: 5
  source_sha256: b66fe308f21f87d7cf5a6ce5a9f6ab74f4d86344c6a8c73085c5f72d46352e94
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define Workspace

## Claim

### Prose Claim

A Workspace is the Workbench context for one selected Project. In an existing native Codex chat, it binds to the host-supplied native thread reference; that reference is required only in native mode and is never invented or reused from another chat. In standalone browser mode, it uses the existing browser-owned Workspace/session ID without a native chat or an invented native thread reference. It keeps at least one View. It does not create a second conversation history or a standalone chat.

### Formal Claim

```python
from dataclasses import dataclass, field
from anechoic.formal_claims import Cardinality, declare_entity


@dataclass
class Workspace:
    native_thread_id: str = field(metadata={
        "property_occurrence_cardinality": Cardinality(minimum=0, maximum=1),
        "value_cardinality": Cardinality(minimum=0, maximum=1),
    })
    project_root: str = field(metadata={
        "property_occurrence_cardinality": 1,
        "value_cardinality": 1,
    })


declare_entity(
    entity_name="Workspace",
    entity_class=Workspace,
    incoming_model_relations=({
        "source": "View",
        "relation": "IS_CONTAINED_BY",
        "source_cardinality": 1,
        "target_cardinality": Cardinality(minimum=1, maximum=None),
    },),
)
```
