---
atom_family: TKT
atom_id: AN-T-2563
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

Verify accepted subject-family layers independently

# Summary

Verify accepted subject-family layers independently

## Objective

Independent checks reject wrong or missing subject-family layers while accepting exact prospective outputs.

## Details

Estimated own work: at most 15 minutes. Follow `_projection/core-entity-review/stage2/working-ledger.followups-2094-2099.contract.md`. Own only support/verify_working_mapping_ledger.py and support/test_working_mapping_ledger.py. Extend the existing independent one-off verifier and its focused tests for the six exact selected layers, without importing the producer. Enumerate current source origins and verify exact selected coverage, accepted report/receipt provenance, layer order, final target/confidence and complete quarantine/lineage preservation. Add valid-control adversarial cases for omitted layer, missing/extra or stale origin, wrong target and bad acceptance pins. No output replacement.

Workers are not alone. Root owns acceptance, lifecycle and a commit after completion. Preserve all unrelated work, original authority and frozen evidence. No MCP/FPF/runtime or source adoption.

### Completion

The independent ad-hoc verifier requires complete accepted research coverage, exact per-row provenance and final decisions/targets/confidence. Eighteen focused tests pass. Root's complete prospective live ledger and ten deliberately wrong variants confirm acceptance and fail-closed behavior, including omission of all six layers. Historical fixture roots without accepted receipts remain isolated; the real old draft correctly fails until rebuild. Exact verification is recorded in `_projection/core-entity-review/stage2/task-2101.receipt.json`.

### Definition of Done

Not Done if assigned output/checks are missing or stale, selected ownership/provenance or meaning is lost, wrong data passes, original authority changes, completion exceeds actual evidence, or work exceeds the bound without decomposition.
