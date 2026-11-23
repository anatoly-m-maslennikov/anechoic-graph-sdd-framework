---
subject_scopes:
  - relation-model
version: 2
updated_at: 2026-08-19 01:11:46
llm_session_ids:
  - codex:019f591f-04f6-70f2-8de7-828b7cccc69d
relations:
  child_of:
    - ANECHOIC-META-REQU-706--make-structural-ownership-immediate-recursive-and-typed
---
# Derive inverse structural ownership

ANECHOIC must derive the inverse `structural_children` view from stored `structural_parent` relations and must not persist that inverse separately.
