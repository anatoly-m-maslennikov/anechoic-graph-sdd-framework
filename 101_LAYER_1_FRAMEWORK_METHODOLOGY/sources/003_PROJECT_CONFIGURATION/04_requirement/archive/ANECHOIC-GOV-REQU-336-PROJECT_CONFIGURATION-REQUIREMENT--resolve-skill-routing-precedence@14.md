---
subjects:
  governs: "ANECHOIC Routing Tree"
  depends_on:
    - "ANECHOIC Main Skill"
    - "ANECHOIC Direct Route Skill"
    - "Project Configuration"
version: 14
updated_at: "2026-09-17 12:43:59 +0000"
relations: {}
---
# Resolve skill routing precedence

Skill routes **must** resolve by explicit precedence: project-local ANECHOIC routes override framework routes, which override provider-global routes.
