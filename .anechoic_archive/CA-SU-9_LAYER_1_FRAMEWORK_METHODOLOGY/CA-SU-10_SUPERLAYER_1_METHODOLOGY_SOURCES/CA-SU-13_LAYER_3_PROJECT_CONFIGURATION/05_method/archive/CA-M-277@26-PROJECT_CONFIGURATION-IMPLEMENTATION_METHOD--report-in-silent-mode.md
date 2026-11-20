---
subjects:
  governs: 'Subject/ANECHOIC/Graph/Node/Project Model/Project.Framework Settings.Interaction.Reporting Mode: silent'
  depends_on:
  - Subject/ANECHOIC/Graph/Node/Project Model/Project.Framework Settings.Interaction.Reporting Mode
  - Subject/ANECHOIC/Graph/Node/Project Model/Project.Framework Settings.Interaction.Reporting Mode.Effects
  - Subject/ANECHOIC/Graph/Node/Project Model/Project.Framework Settings.Interaction.Reporting Mode.Mandatory Information
  - Subject/ANECHOIC/Graph/Node/Project Model/Term//Artifact
  - Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Architecture/Communication
  - Subject/ANECHOIC/Graph/Node/Project Model/Project
version: 26
updated_at: 2026-10-27 19:59:41 +0400
relations:
  depends_on:
  - CA-R-1440
atom_id: CA-M-277@26
content_role: Method
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
status: Archived
author: Anatoly Maslennikov
tier: 3
type: Implementation Method
---
# Summary

Report **in** silent mode

## Scope

silent-mode reporting.

## Claim

**to** report **in** `silent` mode, answer exploratory input normally **and**, apart from the mandatory information governed by CA-R-1440-CORE_META_MODEL-GENERAL-REQUIREMENT--preserve-mandatory-information-in-every-reporting-mode, report **only** durable Artifacts **or** Project state that ANECHOIC created, updated, archived, committed, **or** **otherwise** changed; omit ordinary announcements of mode selection, workflow routing, Skill chaining, **and** gate transitions.

## Details
