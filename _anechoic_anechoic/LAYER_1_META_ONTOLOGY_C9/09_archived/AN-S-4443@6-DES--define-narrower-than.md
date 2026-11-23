---
atom_family: SPEC
atom_id: AN-S-4443
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-11-05 06:30:39 +0400
---
## Summary

Define NARROWER_THAN

## Claim

### Prose Claim

NARROWER_THAN relates a narrower MODEL kind to a broader MODEL kind. A Property does not narrow. Both endpoints are MODEL kinds; Property bearers and instance populations do not become kinds through this notation. The narrower kind inherits applicable Relation and Property constraints without cloning declarations or instance facts. HAS_NARROWER is its derived inverse. In `X//Y`, Y is narrower than X; traversal runs from broader to narrower.
### Formal Claim

```CFEL
# model
$host ((NARROWER_THAN)) $target;

$direct[<Relation>, (.Name = NARROWER_THAN)];
$inverse[<Relation>, (.Name = HAS_NARROWER)];

$direct ((HAS_INVERSE)) $inverse;

alias($direct) == "//";

$direct ((HAS_CLASSIFICATION)) Derivation == Direct
```

