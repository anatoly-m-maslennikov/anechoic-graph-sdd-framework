---
atom_family: TKT
atom_id: AN-T-2039
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:48:53.126318+00:00'
---
## Summary

Query error diagnostics echo submitted SQL

## Claim

### Prose Claim

In the ANECHOIC working tree based on `c0b983cb27`, `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/query_store.py` forwards DuckDB exception text and `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/workbench_tools.py` returns it as a diagnostic. A live read-only request with `SELECT missing_review_field FROM atoms` returned `LINE 1: EXPLAIN SELECT missing_review_field FROM atoms` in its diagnostic. CA-D-673@18 and CA-M-462@14 require ordinary responses to omit the full submitted SQL. The binder error can expose that text.
