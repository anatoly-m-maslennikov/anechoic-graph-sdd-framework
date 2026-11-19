---
subject_scope: framework-boundary
version: 1
updated_at: 2026-08-17 19:36:01
llm_session_ids:
  - codex:019f591f-04f6-70f2-8de7-828b7cccc69d
relations:
  child_of:
    - ANECHOIC-REQUIREMENT-META-109-all-governed-artifacts-live-under-anechoic
---

# Requirement — Give every runtime-writing script one folder

Each ANECHOIC script or executable tool that persists runtime files owns one
dedicated directory below `.anechoic_runtime/`. All runtime files created by
that script stay inside its directory. Concurrent invocations may use bounded
run-specific descendants of the same script directory.

A script must not scatter runtime files across `.anechoic_runtime/`, write into
another script's directory, or depend on an unowned shared directory. A shared
runtime service is treated as its own executable owner with its own directory;
clients access it through the service contract rather than its files.

## Primary claim

One runtime-writing script or executable tool owns exactly one dedicated
`.anechoic_runtime/` directory namespace.
