---
subjects:
  governs: ANECHOIC Routing Tree
  depends_on:
  - ANECHOIC Main Skill
  - ANECHOIC Direct Route Skill
  - Project Configuration
version: 18
updated_at: 2026-10-24 00:38:25 +0400
relations: {}
atom_id: CA-R-1641@18
content_role: Requirement
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
status: Archived
author: Anatoly Maslennikov
tier: 3
---
# Summary
Resolve skill routing precedence

## Scope
skill route resolution.

## Claim

skill routes **must** resolve by explicit precedence: project-local ANECHOIC routes override framework routes, which override provider-global routes.

## Details
