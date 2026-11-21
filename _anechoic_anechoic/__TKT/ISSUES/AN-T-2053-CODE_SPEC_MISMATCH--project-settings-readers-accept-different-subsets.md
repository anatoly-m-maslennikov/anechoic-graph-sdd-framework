---
atom_family: TKT
atom_id: AN-T-2053
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:53:38.937312+00:00'
---
## Summary

Project Settings readers accept different subsets

## Claim

### Prose Claim

CA-M-284@31 requires one complete validated immutable Project Settings snapshot. `FEATURE_TOOLS/project_selection.py` validates the Project name and paths, `project_settings_values.py` can read a fallback directly, and `compile_applicable_methodology.py` performs a separate TOML read on the release path. The complete schema parser has no production caller. The same Settings can therefore receive different checks across components.
