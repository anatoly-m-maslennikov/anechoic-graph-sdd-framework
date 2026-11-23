---
subject_scope: framework-boundary
version: 1
updated_at: 2026-08-17 19:36:01
llm_session_ids:
  - codex:019f591f-04f6-70f2-8de7-828b7cccc69d
relations:
  child_of:
    - ANECHOIC-META-REQU-085--separate-active-authority-from-preserved-history
    - ANECHOIC-REQUIREMENT-META-109-all-governed-artifacts-live-under-anechoic
---

# Requirement — Isolate runtime state under `.anechoic_runtime`

Every ANECHOIC-owned runtime file lives under the current project's
`.anechoic_runtime/` root whenever the host platform and invoked dependency
permit that location. Runtime files include process state, checkpoints, caches,
temporary materializations, recovery data, generated scratch, and other
reconstructible execution state.

When an operating system or external tool requires its native temporary or
cache location, ANECHOIC stores only the minimum transient adapter state there,
never treats it as governed authority, and cleans or reconciles it when the
owning operation ends. Runtime placement must not create files in ambient
repository directories.

The complete `.anechoic_runtime/` tree remains non-authoritative: deleting it
may lose resumable progress or caches, but must not lose any governed artifact.

## Primary claim

ANECHOIC-owned reconstructible execution state is isolated under
`.anechoic_runtime/` whenever technically possible.
