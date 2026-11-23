---
atom_family: TKT
atom_id: AN-T-3022
container:
  component: C16
priority: 2
context:
  template: problem
state:
  status: archived
  version: 1
  updated_at: 2026-10-06 03:53:17 +0000
---
## Summary

Reject occupied Create destinations

# Summary

Reject occupied Create destinations

## Concern

W01 treats any occupied destination as duplicate without proving equivalent intent or bytes; the selected executor turns that into a successful no-op.

## Evidences

At commit `c011b68fa`, `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/lifecycle_intents.py:749-751` returns pathname-only duplicate; `203_APPS/WORKFLOW_ORCHESTRATOR/selected_execution.py:293-295` terminalizes it as no_op. CA-O-128 requires destination absence/unused identity. Regression: `201_TOOLS/tests/test_lifecycle_create_conflicts.py`.

Source/mock results do not establish actual release completion.

## Blast radius

The affected selected Workflow, full release gate and CA-P-1655 final acceptance.

## Disposition

Reject destination collision before effects under O128; retain the existing carrier and test the conflict.

CA-P-1758 owns the bounded repair. Keep this Problem active until its regression and independent acceptance establish the repair.
