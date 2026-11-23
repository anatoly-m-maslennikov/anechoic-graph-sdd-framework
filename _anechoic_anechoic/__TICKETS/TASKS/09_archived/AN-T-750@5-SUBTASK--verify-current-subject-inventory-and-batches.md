---
atom_family: TKT
atom_id: AN-T-750
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 08:22:45 +0400
---
## Summary

Verify current Subject inventory and batches

# Summary

Verify current Subject inventory and batches

## Objective

Independently verify exact source and occurrence coverage and prove corrupted data is refused.

## Details

Estimated own work: 15 minutes. Inherit CA-P-1959 and CA-P-1972 boundaries. This decomposition records the expanded preparation work; it does not pretend the rejected first inventory was accepted.

Prerequisite: CA-P-1988 Done. Own the independent verifier and its isolated tests. Re-enumerate sources and reconstruct occurrences without importing the producer. Compare Structure/candidate/review/current source pins, every field/index/value and all exclusions/findings. Verify each selected source and occurrence belongs to one bounded batch. Deliberately remove/corrupt an occurrence or source pin and require refusal. Check actual newline-bearing file hashes, not guessed serialization. Output: support/verify_current_inventory.py, support/test_current_inventory.py and its actual read-only verification receipt.

Root owns shared integration and Git. Preserve other workers' edits. Use uv and .anechoic_tmp for scratch. No MCP/FPF, authority, runtime or captured-review mutation. Creating this Plan does not complete its checks.

### Definition of Done

Not Done if the required evidence/output is missing or stale, coverage or independent checks fail, a Source or captured artifact changes, unsupported authority/adoption is claimed, or own work exceeds 15 minutes without decomposition.
