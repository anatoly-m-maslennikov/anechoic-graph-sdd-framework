---
identity:
  atom_id: AN-S-280
context:
  container:
    component: C37
  tier: 4
  lens: QA
state:
  status: active
  version: 18
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Validate complete reproducible Entity and Term graph output

# Validate complete reproducible Entity and Term graph output

## Test case

Generate twice from identical fixtures containing declared Terms, one parent chain, direct dependencies with transitive closure, an unresolved reference, a dependency cycle, a cardinality violation, **and** an unparseable Carrier.

## Acceptance criteria

the two semantic outputs are byte-identical **and** stably ordered. They contain **every** declared Term, direct parent, direct edge, closure edge, cycle, violation, unresolved reference, unparseable region, source path **and** digest, frontier identity, settings digest, **and** explicit non-authoritative status.
