---
atom_id: CA-R-2960
ref_id: CA-R-2960@1-draft
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Node//Continuant//Actor//AI Agent//Main Agent
tier: 3
status: Draft
version: 1
updated_at: 2026-11-05 20:56:40 +0400
carrier_destination:
  file:
    name: CA-R-2960@1-draft-CORE_META_MODEL-DECLARATION--declare-main-agent.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---

## Summary

Declare Main Agent

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import AIAgent

class MainAgent(AIAgent):
    pass

declare_entity(entity_class=MainAgent, entity_name="Main Agent")
```

## Semantics

A Main Agent is the AI Agent responsible for the overall assigned work.
