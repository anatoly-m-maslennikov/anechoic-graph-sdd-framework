---
subjects:
  governs: "ANECHOIC Routing Tree"
  depends_on:
    - "ANECHOIC Main Skill"
    - "ANECHOIC Direct Route Skill"
    - "Project Configuration"
version: 16
updated_at: "2026-09-17 12:43:59 +0000"
relations: {}
atom_id: "ANECHOIC-GOV-REQU-336"
content_role: "Requirement"
current_scope_unit: "PROJECT_CONFIGURATION"
claim_target_scope_unit: "PROJECT_CONFIGURATION"
local_tier: "Standard"
status: "Active"
author: "Anatoly Maslennikov"
type: "Requirement"
global_tier: 11
---
# Resolve skill routing precedence

Skill routes **must** resolve by explicit precedence: project-local ANECHOIC routes override framework routes, which override provider-global routes.
