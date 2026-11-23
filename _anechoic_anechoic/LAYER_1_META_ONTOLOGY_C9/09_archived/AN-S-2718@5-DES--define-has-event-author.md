---
atom_family: SPEC
atom_id: AN-S-2718
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Define HAS_EVENT_AUTHOR

## Claim

### Prose Claim

HAS_EVENT_AUTHOR identifies the Actor who performed the recorded event.

Forward `Host ((HAS_EVENT_AUTHOR)) Target` and reverse `Target <((HAS_EVENT_AUTHOR)) Host` are views of the same Relation fact.
HAS_EVENT_AUTHOR relates Event Record instance to Actor instance.
### Formal Claim

```CFEL
# model
Relation//HAS_EVENT_AUTHOR ((HAS_INVERSE)) Relation//IS_EVENT_AUTHOR_OF;

Relation//HAS_EVENT_AUTHOR ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Event Record//$event_record ((HAS_EVENT_AUTHOR)) Actor//$actor;
```

