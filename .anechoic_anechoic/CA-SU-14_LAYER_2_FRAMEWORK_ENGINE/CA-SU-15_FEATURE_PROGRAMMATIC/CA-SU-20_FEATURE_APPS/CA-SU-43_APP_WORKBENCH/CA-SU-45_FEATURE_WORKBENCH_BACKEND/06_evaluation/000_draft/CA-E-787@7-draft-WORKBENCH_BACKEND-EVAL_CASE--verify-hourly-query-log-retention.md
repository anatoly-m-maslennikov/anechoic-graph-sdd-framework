---
identity:
  atom_id: CA-E-787
  ref_id: CA-E-787@7-draft
context:
  container:
    scope_unit: CA-SU-45
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
      <+ Observability <+ Logging
    dependencies:
    - MODEL//ANECHOIC <+ Projection
  tier: 5
relations:
  evaluation_for:
  - CA-R-2903
  IS_REPLACEMENT_FOR:
  - CA-E-787
state:
  status: draft
  version: 7
  updated_at: '2026-11-13T20:51:17.423875+00:00'
destination:
  file:
    name: CA-E-787@7-draft-WORKBENCH_BACKEND-EVAL_CASE--verify-hourly-query-log-retention.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/06_evaluation/000_draft
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Verify hourly query-log retention

## Claim

### Prose Claim

Use the real backend to verify that adjacent UTC hours append NDJSON to their respective `query-log-YYYY-MM-DD-HH.ndjson` files. Each retained record has exactly `log_id`, `at`, `sql`, `outcome`, `error`, `row_count` and `column_count`. Records younger than 48 hours remain listable and gettable. Records at or beyond 48 hours disappear during append, list or get retention.

Legacy `query-log.json` remains byte-identical and listable and gettable beside hourly records. No record is appended, migrated or backfilled there. Successful or failed Run submits once to an ordered background writer after synchronous Save. Check submits none, and Run returns without waiting. Writer failure reports stderr without retry or warning and preserves the completed result.

Expiry does not alter saved Views or Journal, watcher log or result cache. Verify backend and MCP rollover and legacy cases. Orderly shutdown drains submitted history. A crash may lose unflushed history but not sources or saved items.
