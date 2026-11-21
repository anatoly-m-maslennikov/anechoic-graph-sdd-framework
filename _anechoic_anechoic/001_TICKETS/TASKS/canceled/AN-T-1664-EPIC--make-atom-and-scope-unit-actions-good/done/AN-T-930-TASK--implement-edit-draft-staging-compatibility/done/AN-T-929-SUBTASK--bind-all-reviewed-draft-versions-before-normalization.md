---
atom_family: TKT
atom_id: AN-T-929
container:
  atom: AN-T-930
priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 5
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Bind all reviewed Draft Versions before normalization

## Objective

Require carried YAML Version to equal the materialized canonical candidate/explicit Version binding for legacy and ID-free reviewed Subject Drafts, before normalization can erase a mismatch.

## Details

At most 15 minutes own work; split before extending. Independent P2466 review confirmed R866 requires Version-drift refusal for every Draft-backed promotion input. P2473 qualified-marker checks remain correct; extend the shared candidate boundary rather than duplicate normalization. Add legacy and ID-free repinned Version-drift regressions while retaining positive compatibility/no-op coverage.

### Definition of Done

Focused synthetic-project checks and independent review verify the stated behavior without live MCP tests, deployment, migration, or held-batch replay. Review dependent next Task before acceptance execution.

### Verified execution checkpoint

All reviewed formats bind strict positive carried Version to the materialized candidate before normalization. Repinned legacy and ID-free drift regressions and positive/no-op cases passed: focused 16, contract 5, workflow 10. Independent review closed the Version-drift findings with no actionable defect.
