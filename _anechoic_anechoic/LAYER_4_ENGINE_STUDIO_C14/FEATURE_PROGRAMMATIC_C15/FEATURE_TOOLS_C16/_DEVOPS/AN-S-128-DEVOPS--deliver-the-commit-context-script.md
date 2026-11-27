---
atom_family: SPEC
atom_id: AN-S-128
container:
  component: C16
tier: 2
context:
  lens: DevOps
state:
  status: active
  version: 36
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---
## Summary

Deliver the commit-context script

# Deliver the commit-context script

COMMIT_CONTEXT **must** be delivered through the canonical source script `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/COMMIT_CONTEXT/commit_context.py` **and** its content-identical Carrier **in** the selected `.anechoic_runtime/tools` release.

- expose the common read-only Finder CLI contract. the standalone script **and** the logic used by COMMIT_CHANGE_SET **must** call the same release-local non-executable implementation **and** return the same sealed context for identical inputs **and** unchanged observed state.
- Apply AN-S-5174 to sealing a COMMIT_CONTEXT observation.
