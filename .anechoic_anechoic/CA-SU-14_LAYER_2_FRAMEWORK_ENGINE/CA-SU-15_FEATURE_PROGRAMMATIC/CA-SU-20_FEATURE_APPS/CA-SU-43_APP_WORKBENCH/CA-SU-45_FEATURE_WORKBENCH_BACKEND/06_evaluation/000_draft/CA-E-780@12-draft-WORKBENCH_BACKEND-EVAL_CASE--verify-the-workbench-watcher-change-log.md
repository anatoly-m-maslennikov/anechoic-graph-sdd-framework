---
identity:
  atom_id: CA-E-780
  ref_id: CA-E-780@12-draft
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
  tier: 6
relations:
  evaluation_for:
  - CA-R-2950
  - CA-R-2724
  - CA-C-704
  IS_REPLACEMENT_FOR:
  - CA-E-780
state:
  status: draft
  version: 12
  updated_at: '2026-11-13T20:51:11.392937+00:00'
destination:
  file:
    name: CA-E-780@12-draft-WORKBENCH_BACKEND-EVAL_CASE--verify-the-workbench-watcher-change-log.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/06_evaluation/000_draft
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Verify the Workbench watcher change log

## Claim

### Prose Claim

With the existing `watchdog` Observer limited to the selected repository `control_root`, verify NDJSON and DuckDB `change_log` retain the same technical rows. Native add, modify and delete produce `create`, `update` and `remove`. Same-parent move is `rename`, parent-changing move is `move`, and boundary entry or exit is `create` or `remove`. Directory create, move and remove are recorded and indexed; directory-modification noise and outside-root changes are not. Add and delete without a native move callback remain two observations, never an inferred rename or move.

Preserve every grouped observation without Workflow or Journal invention. The existing owner loop performs same-thread idle cleanup: rows expire after 48 hours, and the oldest rows are removed from both stores at 100,000 rows. Restart or full reread rehydrates live rows under the same limits. A failed source or log write follows the existing error boundary, without an error event row, Journal, watcher service, scheduler, retry or recovery.

## Details

Use a real Docker bind-mounted temporary repository and actual creation, edit, rename, move, directory and boundary operations. Wait through the owner loop and verify matching callback paths and file and table rows. Prove `change_log` is not an `atoms` or `scope_units` source, graph vertex or Relation fact, and exposes only `observed_at`, `operation`, `old_path` and `new_path`.

Seed a deterministic valid 5,000-Atom inventory and use it for E2E mutations and visibility timing. A result is visible only with exact ID, version, path, Header.Container and required direct and derived facts; event-log visibility or counts alone do not pass. Report structured fixture, image, operation, count and elapsed metrics from mutation to query-visible result, with 500-file throughput as 500/elapsed.

Hard limits are ordinary mutation <=1.5s; 500 add, update or delete <=15s; 500 move or filename rename, including required carrier metadata, <=30s; and combined rename plus Header/content update <=30s. Observation timeout is separate. No variable may raise or disable the limits. Distinguish fixture and repository timing and preserve correctness deadlines.
