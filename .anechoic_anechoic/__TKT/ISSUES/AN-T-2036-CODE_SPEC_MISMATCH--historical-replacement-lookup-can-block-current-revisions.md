---
atom_family: TKT
atom_id: AN-T-2036
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:43:43.918340+00:00'
---
## Summary

Historical replacement lookup can block current revisions

## Claim

### Prose Claim

In the ANECHOIC working tree based on commit `c0b983cb27`, `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE/publish.py`, `update_atom` and `resolve_replacement`, reselect historical targets of retained replacement links before archiving a Current revision. `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/service.py`, `lifecycle_archive_candidates`, selects indexed or admitted Archive locations.

The local MCP refused content-only revisions of CA-M-509@6, CA-R-1114@24 and CA-R-1901@19 with `Replacement target cannot be resolved safely`, before any write. CA-D-705 and CA-M-176 had no query-visible Archive row after loading their declared Scope and Role. CA-R-1901 also retains CA-D-594 under a retired Scope. CA-R-1105@31 defines an exact Current-to-Draft Update and CA-M-1006@7 requires explicit selection errors. The retained lineage prevented promotion and the response did not identify which source failed.
