---
atom_family: SPEC
atom_id: AN-S-2998
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T17:41:18.752584+00:00"
---
## Summary

Declare AI Agent

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Actor

class AIAgent(Actor):
    pass

declare_entity(entity_class=AIAgent, entity_name='AI Agent')
```

## Semantics

An AI Agent is an Actor that performs delegated work using an AI model.
