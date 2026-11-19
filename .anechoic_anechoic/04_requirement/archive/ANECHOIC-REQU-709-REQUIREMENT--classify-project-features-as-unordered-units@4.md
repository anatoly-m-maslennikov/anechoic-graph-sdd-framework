---
atom_id: ANECHOIC-REQU-709
subject_scopes:
  - scope-topology
version: 4
updated_at: 2026-09-06 01:45:12 +0400
llm_session_ids:
  - codex:019f591f-04f6-70f2-8de7-828b7cccc69d
relations:
  child_of:
    - ANECHOIC-REQU-032-CORE-REQUIREMENT--let-parents-own-immediate-child-goals
---
# Classify Project Features as unordered units

Every ANECHOIC Feature is an `unordered_unit`, is owned by exactly one immediate Structural unit, and has no `local_order`. A Feature owned directly by ANECHOIC is at Structural level `1`; a Layer-owned Feature is at Structural level `2`.
