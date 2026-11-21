---
atom_family: SPEC
atom_id: AN-S-2199
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 5
  updated_at: '2026-11-13T04:20:57.712025+00:00'
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
