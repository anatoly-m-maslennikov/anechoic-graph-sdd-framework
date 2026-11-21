---
atom_family: TKT
atom_id: AN-T-749
structure:
  container:
    atom: AN-T-1608
  priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 6
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Compare current sources with captured evidence

## Objective

Show where current source bytes match or differ from the frozen snapshot, without replacing either evidence set.

## Details

Estimated own work: 15 minutes. Inherit CA-P-1959 and CA-P-1972 boundaries. This decomposition records the expanded preparation work; it does not pretend the rejected first inventory was accepted.

Verify immutable Git pins at a971d0e00c33c779f485fc8cad63194894d440fb and fresh current registered Core pins. Compare full bytes, Subjects and Main Content by ID. Report same, changed, new and missing, with exact separate evidence. Do not infer a mapping from byte equality. Output: support/compare_current_snapshot.py and current-snapshot.delta.json. Reconcile current inventory source pins explicitly; keep any captured baseline-count discrepancy visible.

Root owns shared integration and Git. Preserve other workers' edits. Use uv and .anechoic_tmp for scratch. No MCP/FPF, authority, runtime or captured-review mutation. Creating this Plan does not complete its checks.

### Definition of Done

Not Done if the required evidence/output is missing or stale, coverage or independent checks fail, a Source or captured artifact changes, unsupported authority/adoption is claimed, or own work exceeds 15 minutes without decomposition.
