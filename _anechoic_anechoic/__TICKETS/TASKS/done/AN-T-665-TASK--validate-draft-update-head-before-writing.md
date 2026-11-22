---
atom_family: TKT
atom_id: AN-T-665
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: done
  version: 8
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Validate Draft Update head before writing

## Objective

Within <=10 minutes, validate the current Draft head before any Update effect.

## Details

Own only lifecycle_intents.py and tests/test_draft_promotion_golden.py. The current native review rejects the Update path because it loads an unrelated supplied parent without validating that parent against the actual current Draft. Call the supported unique current-head validator before reserving or writing; only its validated result may parent the update. Reject unrelated valid head substitution, stale same-path replay and mismatching current bytes with no Project changes. Preserve successful Create/Update/demotion/promotion/recovery and shared changed-carrier behavior. Golden first, then actual designated-worker focused tests; no source/Plans/Git/real-project/image changes or C447/C449 workaround.

## Definition of Done

Actual substitution/replay unchanged-tree regressions and existing native/status cases pass with exact hashes, permitting the required narrow independent re-review.

### Current accepted completion

Independent review ACCEPT98% confirms the pre-write current-target head validation. Nine native promotion/Update and fourteen model-status tests pass. The former unrelated-head mutation probe now returns draft-lineage-invalid with whole-Project bytes unchanged; stale/replayed heads also refuse. Current working lifecycle_intents.py de56ce720bfa9f29ba728d3c56db45ff9991e069f20fcd613fee73563dcdfb2d; native goldens 0a56ca2c3e27ec91650b1878ea008fa9caec7eb256169005e2bc15bfaa77f64d.
