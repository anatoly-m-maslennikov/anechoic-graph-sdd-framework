---
atom_family: TKT
atom_id: AN-T-821
container:
  component: C14
priority: 2
context:
  template: task
state:
  status: archived
  version: 3
  updated_at: 2026-10-24 06:04:39 +0400
---
## Summary

Assess the complete RMED input

# Summary

Assess the complete RMED input

## Objective

Provide a Step that reports conflicts, gaps and ambiguity across the prepared R, M, E-policy and D projections before implementation.

## Details

Check that the four projections cover the same requested implementation boundary, have confirmed saved-output references and preserve actual Read current_state/source-view evidence. Incomplete Query/Read coverage or unconfirmed output persistence blocks affected work. Compare source evidence through the accepted read/currentness bindings; do not assume an Atom ID and Version alone prove unchanged source. Check R-versus-M, R-versus-E and R-versus-D consistency as well as issues inside each projection. Return the exact question, affected original sources, impact and suggested resolution where evidence supports one. Blocking ambiguity or incomplete inputs are reported to the Operator; implementations do not repair projections by silently rewriting sources. If a source changes during a Run, stop affected work and regenerate the affected projection before continuing.

Execute this Task in its own subagent. Preserve unrelated work; the integration owner controls shared files and Git. Split only genuinely oversized own-work into smaller P Tasks before execution. This Task grants no live operation outside the selected implementation scope.

## Definition of Done

Positive and conflicting/incomplete/stale-input fixtures produce truthful dispositions and prevent dependent effectful work from consuming unresolved blocking inputs.

