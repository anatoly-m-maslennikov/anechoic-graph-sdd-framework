---
atom_family: SPEC
atom_id: AN-S-2720
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Define RUNS

## Claim

### Prose Claim

RUNS binds a Step or Substep invocation to its execution target. Its inverse is IS_RUN_BY.
### Formal Claim

```CFEL
# model
Relation//RUNS ((HAS_INVERSE)) Relation//IS_RUN_BY;

Relation//RUNS ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Step//$step ((RUNS)) (in (Action, Workflow))//$selected;

Substep//$substep ((RUNS)) Action//$action;
```

