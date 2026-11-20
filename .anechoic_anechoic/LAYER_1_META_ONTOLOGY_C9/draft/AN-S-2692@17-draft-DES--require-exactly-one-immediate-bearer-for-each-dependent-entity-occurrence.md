---
identity:
  atom_id: AN-S-2692
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: draft
  version: 17
  updated_at: 2026-11-05 04:29:34 +0400
---
## Summary

Require exactly one immediate bearer for each dependent Entity occurrence

## Claim

### Prose Claim


Model Property occurrences selected by `Node.**` and their direct IS_PROPERTY_OF connections.


Every source-declared model Property occurrence selected by `Node.**` must have exactly one immediate bearer, identified by one outgoing direct IS_PROPERTY_OF connection to that bearer. A source establishes dependence independently of whether the edge is present, so a missing edge fails this requirement. Select source-declared Property occurrences independently of whether their bearer edges exist; do not infer dependence from edges or create a bearer connection.

## Semantics

`Node.**` selects Properties of Node and its narrower branch, grounded in bearer dependence through IS_PROPERTY_OF. Property instances are distinct from model Properties; their HAS_INSTANCE permissions are declared separately. Its lexical Term is separately defined at `Term//Property`. Identifying a source-declared Property occurrence does not invent a bearer edge or treat a missing edge as proof of independence. The Property occurrence has identity qualified by its immediate bearer; the Property definition supplies its value Format and direct-value cardinality. The bearer-Relation count is distinct from the number of values a Property allows.

## Details

This Rule applies to source-declared Properties covered by `Node.**`. Identify the source-declared occurrences independently of their IS_PROPERTY_OF edges. Missing required bearer edges remain failures; this Rule does not infer or create edges.
