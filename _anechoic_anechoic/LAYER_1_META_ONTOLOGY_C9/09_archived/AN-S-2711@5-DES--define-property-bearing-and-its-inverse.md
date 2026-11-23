---
atom_family: SPEC
atom_id: AN-S-2711
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

Define Property bearing and its inverse

## Claim

### Prose Claim

IS_PROPERTY_OF directs a Property to exactly one immediate bearer. HAS_PROPERTY is its derived inverse. The bearer relation is acyclic. `Bearer.Property` addresses the Property.

A Property has exactly one immediate bearer; the bearer may be any applicable declared model Entity or instance.

Forward `Host ((IS_PROPERTY_OF)) Target` and reverse `Target <((IS_PROPERTY_OF)) Host` are views of the same Relation fact.
In `X.Y`, Y IS_PROPERTY_OF X; traversal runs from bearer to Property.
IS_PROPERTY_OF relates Property to immediate bearer.
### Formal Claim

```CFEL
# model
$property ((IS_PROPERTY_OF)) $bearer;

Relation//IS_PROPERTY_OF ((HAS_INVERSE)) Relation//HAS_PROPERTY;

alias(Relation//IS_PROPERTY_OF) == ".";

Relation//IS_PROPERTY_OF ((HAS_CLASSIFICATION)) Derivation == Direct
```

