---
atom_family: TKT
atom_id: AN-T-754
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: done
  version: 7
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Reject omitted mapping layers in independent verification

## Objective

The one-off working ledger fails the concrete incorrect-data cases found in Root review.

## Details

Estimated own work: at most 15 minutes. Read working-ledger.contract.md. Correct the independent checker so it reconstructs every required selected layer from frozen inputs, compares exact baseline decisions and the last applicable decision/target/confidence, rejects dropped required layers and wrong baseline outputs, checks accepted receipt/report identity and exact Actor subset coverage/targets, and keeps the five unaccepted grammar-source rows null. Add isolated omission, true wrong-target and wrong-baseline negatives. Do not import the consolidator or mutate its outputs. Own stage2/support/verify_working_mapping_ledger.py and test_working_mapping_ledger.py. Root owns independent live integration and Plan/Git.

Workers are not alone. Preserve original Core Subjects/content, captured reports, frozen baseline, unrelated work and the existing guarded migration route. No MCP/FPF/runtime, selector adoption, native admission or authority writes. Root owns receipts, lifecycle and a commit after each Task. If the bound is exhausted, return partial evidence for decomposition.

### Completion

The independent verifier reconstructs frozen/current counterpart lineage, every required review layer and final target/confidence, receipt acceptance and all 43 Actor targets. Ten adversarial tests and the intermediate no-grammar-receipt live ledger pass. The now-accepted grammar layer remains assigned to CA-P-2093 before group completion. Exact verification is recorded in `_projection/core-entity-review/stage2/task-2091.receipt.json`.

### Definition of Done

Not Done if the assigned live gate or negative probes fail, expected layers or lineage are missing, guesses are executable, captured/source bytes are changed, or own work exceeds the bound without decomposition.
