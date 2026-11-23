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
  version: 29
  updated_at: 2026-10-30 16:26:18 +0400
---
## Summary

Register depends_on and required_by relation pair

## Claim scope

the `depends_on` **and** `required_by` relation pair.

## Claim

`depends_on` **means** a direct dependency-ordering relation from a dependent Artifact **to** its prerequisite Artifact, with `required_by` as its inverse-derived view. Plan start dependencies use the Plan Graph's `BLOCKS` under CA-R-1580 instead; this Relation Kind **must not** duplicate that scheduling fact.

### Formal claim

```text
Entity/Graph Syntax <+ Relation//depends_on
Entity/Graph Syntax <+ Relation//required_by
```
