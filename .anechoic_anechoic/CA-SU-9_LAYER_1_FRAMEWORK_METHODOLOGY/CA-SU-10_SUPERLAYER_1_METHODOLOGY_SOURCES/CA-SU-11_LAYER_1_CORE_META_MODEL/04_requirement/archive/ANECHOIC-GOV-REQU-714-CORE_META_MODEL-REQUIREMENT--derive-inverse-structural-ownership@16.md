---
subjects:
  governs: "relation-model"
  depends_on:
    - "atom-boundary"
version: 16
updated_at: "2026-09-10 05:08:55 +0400"
relations:
  child_of:
    - ANECHOIC-META-REQU-706
atom_id: "ANECHOIC-GOV-REQU-714"
content_role: "Requirement"
current_scope_unit: "CORE_META_MODEL"
claim_target_scope_unit: "CORE_META_MODEL"
local_tier: "Standard"
status: "Active"
author: "Anatoly Maslennikov"
type: "Requirement"
global_tier: 11
---
# Derive inverse structural ownership

ANECHOIC **must** derive the inverse `structural_children` view from stored `structural_parent` relations **and** **must not** persist that inverse separately.
