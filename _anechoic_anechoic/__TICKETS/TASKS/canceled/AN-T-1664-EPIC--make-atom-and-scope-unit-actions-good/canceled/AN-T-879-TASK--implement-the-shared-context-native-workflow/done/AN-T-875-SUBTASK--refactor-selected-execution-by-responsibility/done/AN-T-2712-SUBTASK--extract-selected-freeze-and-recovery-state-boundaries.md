---
atom_family: TKT
atom_id: AN-T-2712
container:
  atom: AN-T-875
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

Extract selected freeze and recovery state boundaries

## Objective

Separate source freeze, stored request/result and recovery responsibilities through their existing state owners, without new replay, rollback, Journal or permission policy.

## Details

The Operator explicitly refused a source-size exception and selected refactoring legacy files first. Every leaf is at most 15 minutes own work; split before expanding. New or materially changed Python files must meet the applicable <=200 physical-line target and small cohesive unit boundaries; no mixin/namespace class or imported-method facade substitutes for responsibility decomposition. Preserve the pinned C901/format/lint and applicable typing baseline. Use the locked Project virtual environment, disable bytecode writes and keep disposable test state below configured Project Temporary State. Do not revert other workers' changes. One Task per file, exact predecessor history; review/update dependants after each completed Task.

Predecessor graph/admission extraction CA-P-2586 is reviewed Done. Canonical contracts, bounded evidence I/O and finite Run planning are available; continue the state-owner freeze/load/revalidation/dispatch/recovery integration. Preserve intent→accepted→intent-unlink ordering, actual receipts and no replay. This responsibility can proceed alongside independent native-capability and graph-loop extraction; no current Workflow feature is admitted.

### Definition of Done

Retain actual before/after focused tests, changed paths, source/unit/complexity measurements and explicit unresolved limits. Preserve frozen test oracle bytes and current public behavior before new shared-context feature work. No production MCP, release, deployment, full suite, source-policy edits or Git publication.

### Refactor gate checkpoint — 22 October 2026

Canonical freeze/load/revalidation, shared Run sessions, intent/accepted uncertainty handling and graph readback/reconciliation are separated with explicit root/handler/frozen inputs. Preserve intent→accepted→intent-unlink, zero-write readback, current receipts and no replay. The dedicated reconciliation regression, registry/query/error/cancellation checks, complete executor baseline and related recovery checks passed; final independent source/test-seam reviews passed. Subject batches retain their dedicated root-based executor path.
