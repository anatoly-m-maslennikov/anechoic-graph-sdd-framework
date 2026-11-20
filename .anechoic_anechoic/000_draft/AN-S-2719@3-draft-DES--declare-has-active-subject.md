---
identity:
  atom_id: AN-S-2719
context:
  container:
    component: C00
  tier: 3
  lens: DES
state:
  status: draft
  version: 3
  updated_at: 2026-11-03 23:25:51 +0400
---
## Summary

Declare HAS_ACTIVE_SUBJECT

## Claim

### Formal Claim

```CFEL
# model
Relation//HAS_ACTIVE_SUBJECT ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Atom//$atom ((HAS_ACTIVE_SUBJECT)) $active_subject
```

### Prose Claim

HAS_ACTIVE_SUBJECT links an Atom to the declared model entity or instance named by its active Subject. This includes a Requirement/Form Declaration's target and is not restricted to the Node branch. Carrier entities, graph Relation types and their declared instances are admitted when selected by the active Subject. Literal values and CFEL syntax glyphs are not endpoints.

The Host is an Atom and the Target is the entity or instance resolved from its dedicated active Subject field. The field's source supplies the canonical HAS_ACTIVE_SUBJECT fact; obtaining that value from the field does not make this Relation a derived view of another Relation. An unresolved Subject remains a diagnostic, not an empty or automatically valid target population.

Forward `Host ((HAS_ACTIVE_SUBJECT)) Target` and reverse `Target <((HAS_ACTIVE_SUBJECT)) Host` are written views of the same fact. Ownership cardinalities are supplied by their applicable rules; this endpoint signature does not itself create an ownership count.
