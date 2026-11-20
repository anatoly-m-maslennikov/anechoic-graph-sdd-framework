---
atom_family: SPEC
atom_id: AN-S-2673
structure:
  container:
    component: C9
  tier: 2
context:
  lens: DES
state:
  status: active
  version: 28
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Admit typed secondary graph connections

## Claim

### Prose Claim


connections represented by a secondary ANECHOIC Graph.


a secondary ANECHOIC Graph **may** represent typed Relations between its own nodes, **to** another secondary graph **or** its nodes, **and** **to** source Atoms **or** other admitted authoritative sources.

**every** connection **must** identify **`=1`** shared project-unique Relation Type under its defining authority, with its declared direction preserved, **and** must conform to any applicable governing Entity Definition endpoint-class, endpoint-graph-context, **and** cardinality constraints. a graph-qualified reference **or** context may qualify that connection without creating graph-owned Type identity. crossing a graph boundary **must not** create a graph-specific Type identity, import a foreign Relation Type as native, **or** make a referenced external endpoint a native node of the receiving graph. a cross-graph reference preserves the referenced endpoint identity **and** source traceability **without** copying its source fact into independent authority. these permissions do **not** create a Relation Type definition **or** authorize inference beyond the defining authority and applicable Rules.
