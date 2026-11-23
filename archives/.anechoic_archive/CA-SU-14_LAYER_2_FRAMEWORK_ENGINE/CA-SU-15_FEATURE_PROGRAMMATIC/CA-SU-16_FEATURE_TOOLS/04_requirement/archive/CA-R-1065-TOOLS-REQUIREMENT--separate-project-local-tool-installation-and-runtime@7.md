---
subjects:
  declared:
    continuant:
      - feature-boundary
llm_session_ids:
  - codex:019f591f-04f6-70f2-8de7-828b7cccc69d
version: 7
updated_at: 2026-08-23 16:16:20 +0400
---
# Separate project-local Tool installation and runtime

All Tools in one ANECHOIC project must use one project-local installation rooted at `.anechoic_install` and one project-local runtime rooted at `.anechoic_runtime`. The installation contains content-addressed executable releases, shared non-executable libraries, machine-readable registries, declared dependencies, stable launchers, and Hook carriers. The runtime contains only mutable execution state, caches, logs, service state, and other reconstructible outputs.

An installed Tool must import executable and non-executable implementation only from its selected installation release; it must not import framework implementation from the canonical source tree, `.anechoic`, `.anechoic_runtime`, or another project path. Host interpreters and Git remain declared substrate dependencies rather than copied framework implementation. A host-required discovery carrier may point into `.anechoic_install`, but it must contain no independent framework behavior and must not become dependency authority.
