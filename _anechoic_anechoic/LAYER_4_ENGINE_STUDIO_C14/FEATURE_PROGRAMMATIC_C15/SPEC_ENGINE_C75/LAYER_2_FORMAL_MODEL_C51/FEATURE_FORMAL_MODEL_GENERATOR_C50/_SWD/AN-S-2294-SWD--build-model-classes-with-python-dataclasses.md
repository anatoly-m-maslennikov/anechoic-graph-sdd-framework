---
atom_family: SPEC
atom_id: AN-S-2294
container:
  component: C50
tier: 3
context:
  lens: SWD
state:
  status: "active"
  version: 2
  updated_at: "2026-11-24T20:39:11.552611+00:00"
---
## Summary

Build Model classes with Python dataclasses

## Claim

### Prose Claim

- Read Nodes and Properties from `declare_entity` and Relations from `declare_relation` in Python Formal Claims.
- Generate Model classes with strict Pydantic `@dataclass` validation and reject extra fields. Use class inheritance for narrower kinds.
- Keep named instance checks in their Declaring Claims and supply them to MODEL_VALIDATION through its separate checks module.
- MODEL_VALIDATION checks the complete proposed instance at the write boundary. It uses the declared types, allowed values, cardinalities, Relation contracts, and applicable named checks.
