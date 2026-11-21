---
atom_family: SPEC
atom_id: AN-S-2798
container:
  component: C00
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 28
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Qualify Allowed Values with Colon

## Claim

### Prose Claim


allowed-value qualification in a Subject Expression.


**in** a Subject Expression, `X::Y` **must** admit Y as one possible value of X in X's qualified context, irrespective of X's kind or path. This qualification is CFEL syntax, not a graph Relation. It does not assign Y to an occurrence or determine direct-value cardinality.
