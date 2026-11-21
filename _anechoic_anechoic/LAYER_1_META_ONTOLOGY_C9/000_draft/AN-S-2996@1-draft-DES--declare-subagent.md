---
atom_family: SPEC
atom_id: AN-S-2996
structure:
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

Declare Subagent

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import AIAgent

class Subagent(AIAgent):
    pass

declare_entity(entity_class=Subagent, entity_name="Subagent")
```

## Semantics

A Subagent is an AI Agent carrying out work delegated to it by another AI Agent.
