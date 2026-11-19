---
atom_id: ANECHOIC-FRAMEWORK-ENGINE-REQU-562
subject_scopes:
  - session-engine
llm_session_ids:
  - codex:019f591f-04f6-70f2-8de7-828b7cccc69d
version: 3
updated_at: 2026-09-06 01:45:12 +0400
relations:
  child_of:
    - ANECHOIC-GOV-REQU-339-CORE_META_MODEL-REQUIREMENT--register-type-values-for-work-journal-events
    - ANECHOIC-GOV-REQU-340-CORE_META_MODEL-REQUIREMENT--recover-work-journal-coverage-without-invention
    - ANECHOIC-FRAMEWORK-ENGINE-REQU-522--append-work-journal-events
    - ANECHOIC-FRAMEWORK-ENGINE-REQU-523--reconcile-work-journal-coverage
---
# Record governed action lifecycles

The session engine and every Skill that performs governed work must use deterministic Tools to record its start and terminal outcome and to reconcile missing Work Journal coverage after session initialization or context recovery.
