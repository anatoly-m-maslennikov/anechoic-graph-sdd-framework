---
atom_family: SPEC
atom_id: AN-S-2705
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 9
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Define EXECUTES Relation

## Claim

### Prose Claim

EXECUTES connects an actual Runtime to a Workflow Run it executes. The stored direction is Runtime to Workflow Run. IS_EXECUTED_BY is its declared derived inverse and is not a second stored fact.

The Host is an actual Runtime and the Target is the Workflow Run it executes.
Forward `Host ((EXECUTES)) Target` and reverse `Target <((EXECUTES)) Host` are views of the same Relation fact.
EXECUTES relates Runtime to Workflow Run.

#### Details
This named Type uses the general `((RELATION_TYPE))` form. It has no dedicated short Subject operator. This defines the reusable Type and its derived reverse view; it creates no Runtime or actual endpoint tuple.
### Formal Claim

```CFEL
# model
Relation//EXECUTES ((HAS_INVERSE)) Relation//IS_EXECUTED_BY;

Relation//EXECUTES ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
$runtime ((EXECUTES)) $workflow_run
```

