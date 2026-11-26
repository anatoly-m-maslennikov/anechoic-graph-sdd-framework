---
atom_family: SPEC
atom_id: AN-S-3600
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 33
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Register depends_on and required_by relation pair

## Claim

### Prose Claim

#### Claim scope
the `depends_on` **and** `required_by` relation pair.

`depends_on` **means** a direct dependency-ordering relation from a dependent Artifact **to** its prerequisite Artifact, with `required_by` as its inverse-derived view. Plan start dependencies use the Plan Graph's `BLOCKS` under CA-R-1580 instead; this Relation Kind **must not** duplicate that scheduling fact.

Both endpoints are Artifacts: the Host is dependent and the Target is its prerequisite.
Forward `Host ((depends_on)) Target` and reverse `Target <((depends_on)) Host` are views of the same Relation fact.
depends_on relates dependent Artifact to prerequisite Artifact.
### Formal Claim

```CFEL
# model
Relation//depends_on ((HAS_INVERSE)) Relation//required_by;

Relation//depends_on ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
$dependent ((depends_on)) $prerequisite
```

