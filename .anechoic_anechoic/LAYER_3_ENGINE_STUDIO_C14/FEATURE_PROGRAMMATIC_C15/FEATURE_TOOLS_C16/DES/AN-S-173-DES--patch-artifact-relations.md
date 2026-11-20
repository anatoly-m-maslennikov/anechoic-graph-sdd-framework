---
identity:
  atom_id: AN-S-173
context:
  container:
    component: C16
  tier: 1
  lens: DES
state:
  status: active
  version: 23
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Patch artifact relations

# Patch artifact relations

the framework **must** provide one deterministic generic Artifact Tool that adds, replaces, **or** removes explicitly selected typed relation targets **and** `relational_endpoints` descriptors by canonical project-graph node reference, including relative Scope Unit references that use exact full names **and** resolve from the source Artifact owner, while validating permitted relation kind, source **and** target classes, direction, lifecycle, cardinality, Content-role applicability, **and** endpoint identity **without** changing the Artifact body.

this Tool owns generic relation-patch mechanics **only**. it **must not** be exposed **or** applied as a substitute for a ANECHOIC Markdown Atom operation; `ATOM_UPDATE` owns declared Atom updates **and** `REBIND_ATOM_RELATIONS` owns its sealed Atom-rebinding case, including their target, revision, transaction, **and** MCP-gated effect semantics.
