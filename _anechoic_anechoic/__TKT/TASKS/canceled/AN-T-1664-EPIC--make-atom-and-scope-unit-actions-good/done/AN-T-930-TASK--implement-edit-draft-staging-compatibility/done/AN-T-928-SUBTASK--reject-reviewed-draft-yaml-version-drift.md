---
atom_family: TKT
atom_id: AN-T-928
structure:
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

Reject reviewed Draft YAML Version drift

## Objective

Close the independent finding that a qualified Draft marker could disagree with carried YAML Version yet be normalized to a valid candidate.

## Details

At most 15 minutes own work; split before extending. Require marker proposed Version to equal carried YAML Version before candidate normalization. Preserve the already reviewed ID-free/empty-number support and exact source/draft bindings. This is a separate bounded follow-up after P2471 ID-free compatibility.

### Definition of Done

Focused synthetic-project checks and independent review verify the stated behavior without live MCP tests, deployment, migration, or held-batch replay. Review dependent next Task before acceptance execution.

### Verified execution checkpoint

Qualified-marker carried-YAML-Version checks now run before normalization. The repinned marker/YAML mismatch regression and focused staging 14/14 passed, with Ruff and diff checks. Independent review accepted this qualified-format fix and separately assigned all-format legacy/ID-free Version binding to P2476. Parent P2463 remains Active.
