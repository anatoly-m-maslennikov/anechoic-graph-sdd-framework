---
identity:
  atom_id: AN-S-1352
context:
  container:
    component: C43
  tier: 3
  lens: DES
state:
  status: active
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Record observed Workbench source changes in a bounded technical change log

## Claim

### Prose Claim

Expose observed changes only inside selected repository `control_root` as repository-relative `create`, `update`, `rename`, `move`, `remove`. Create/update have new path; remove old; rename/move both. Same-parent basename change is rename; parent change is move even with basename change; entering root is create and leaving is remove. Keep the same retained event set in UTF-8 NDJSON `.anechoic_runtime/workbench/watcher-change-log.ndjson` and read-only DuckDB `change_log`, under 48-hour TTL and 100,000-row cap with oldest/expired rows removed together.

Both stores are technical derived state, not business Journal, Atom/Scope Unit/Relation source or graph fact. `query_schema` exposes only `observed_at`, `operation`, `old_path`, `new_path`; omit identity/error/content/source/Journal/graph fields. Retain equal duplicate events. Record directory create/move/remove and refresh the index, ignore directory-modification noise and outside paths, and never infer move from add/delete. Persist events before refresh; reread the retained log at owner start/full reread. Failures are not event rows.
