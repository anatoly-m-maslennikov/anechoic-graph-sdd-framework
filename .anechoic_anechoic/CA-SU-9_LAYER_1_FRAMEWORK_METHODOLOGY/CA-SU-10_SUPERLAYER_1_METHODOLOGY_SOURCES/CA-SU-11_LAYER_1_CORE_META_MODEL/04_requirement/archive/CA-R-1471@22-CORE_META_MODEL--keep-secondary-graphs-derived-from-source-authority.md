---
subjects:
  governs: Subject
  depends_on:
  - Subject/ANECHOIC/Graph/Rule
  - Subject/ANECHOIC/Graph/Node/Project Model/Projection
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom.Content
  - Subject/ANECHOIC/Graph/Node
  - Subject/ANECHOIC/Graph/Node/Project Model/History/Journal
  - Subject/ANECHOIC/Graph/Relation
version: 22
updated_at: 2026-10-27 19:59:55 +0400
relations: {}
atom_id: CA-R-1471@22
content_role: Requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
status: Archived
author: Anatoly Maslennikov
tier: 1
type: Rule
---
# Summary

Keep secondary graphs derived from source authority

## Scope

secondary ANECHOIC Graphs.

## Claim

secondary ANECHOIC Graphs **must** be Projections derived from their selected authoritative sources **or** source-traceable upstream Projections. their nodes **and** Relations **must** preserve source identities **and** traceability **to** the governing derivation authority **and** source facts.

storing, composing, filtering, **or** rebuilding a secondary graph **must not** make its contents another source of authority. a represented source fact is corrected **at** its authoritative source; an incorrect derivation is corrected under its governing methodology. neither case is resolved by independently editing the projected fact **or** fabricating source history.

## Details
