---
subjects:
  governs: Subject/ANECHOIC/Graph/Relation
  depends_on:
  - Subject
  - Subject/ANECHOIC/Graph/Node/Project Model/Projection
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom
  - Subject/ANECHOIC/Graph/Node
  - Subject/ANECHOIC/Graph/Node/Project Model/History/Journal
  - Subject/ANECHOIC/Graph/Relation
  - Subject/ANECHOIC/Graph/Relation/Type
version: 21
updated_at: 2026-10-27 19:59:55 +0400
relations: {}
atom_id: CA-R-1472@21
content_role: Requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
status: Archived
author: Anatoly Maslennikov
tier: 2
type: Rule
---
# Summary

Admit typed secondary graph connections

## Scope

connections represented by a secondary ANECHOIC Graph.

## Claim

a secondary ANECHOIC Graph **may** represent typed Relations between its own nodes, **to** another secondary graph **or** its nodes, **and** **to** source Atoms **or** other admitted authoritative sources.

**every** connection **must** identify **`=1`** shared project-unique Relation Type under its defining authority, with its declared direction preserved, **and** must conform to any applicable Graph Rule endpoint-class, endpoint-graph-context, **and** cardinality constraints. a graph-qualified reference **or** context may qualify that connection without creating graph-owned Type identity. crossing a graph boundary **must not** create a graph-specific Type identity, import a foreign Relation Type as native, **or** make a referenced external endpoint a native node of the receiving graph. a cross-graph reference preserves the referenced endpoint identity **and** source traceability **without** copying its source fact into independent authority. these permissions do **not** create a Relation Type definition **or** authorize inference beyond the defining authority and applicable Rules.

## Details
