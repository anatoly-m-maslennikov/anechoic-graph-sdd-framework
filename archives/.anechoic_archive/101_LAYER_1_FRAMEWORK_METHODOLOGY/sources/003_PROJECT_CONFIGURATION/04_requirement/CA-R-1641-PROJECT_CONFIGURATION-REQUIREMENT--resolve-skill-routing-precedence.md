---
subjects:
  governs: "ANECHOIC Routing Tree"
  depends_on:
    - "ANECHOIC Main Skill"
    - "ANECHOIC Direct Route Skill"
    - "Project Configuration"
version: 17
updated_at: "2026-09-30 13:09:08 +0000"
relations: {}
atom_id: "CA-R-1641"
content_role: "Requirement"
current_scope_unit: "PROJECT_CONFIGURATION"
claim_target_scope_unit: "PROJECT_CONFIGURATION"
local_tier: "Standard"
status: "Active"
author: "Anatoly Maslennikov"
global_tier: 11
---
# Summary
Resolve skill routing precedence

## Scope
skill route resolution.

## Claim

skill routes **must** resolve by explicit precedence: project-local ANECHOIC routes override framework routes, which override provider-global routes.

## Details
