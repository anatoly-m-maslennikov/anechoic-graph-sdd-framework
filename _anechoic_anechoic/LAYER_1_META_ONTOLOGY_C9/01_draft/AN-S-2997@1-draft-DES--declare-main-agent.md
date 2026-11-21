---
atom_family: SPEC
atom_id: AN-S-2997
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-05 20:56:40 +0400
---

## Summary

Declare Main Agent

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import AIAgent

class MainAgent(AIAgent):
    pass

declare_entity(entity_class=MainAgent, entity_name="Main Agent")
```

## Semantics

A Main Agent is the AI Agent responsible for the overall assigned work.
