---
atom_family: TKT
atom_id: AN-T-936
container:
  component: C15
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 2
  updated_at: '2026-10-20T18:48:24.218Z'
---
## Summary

Preserve Status placement during existing Draft promotion

# Summary

Preserve Status placement during existing Draft promotion

## Objective

Complete destination-aware canonical publication and verified rollback when a non-Active Current Plan is promoted to Active using a reviewed Draft.

## Details

At most 15 minutes own work; split before extending. P2469 partial checkpoint passed Active same-ID V4 publication/exact V3 archive, no-op preservation and injected Draft-cleanup recovery. Reuse the status/bundle owner, preserve children and source pins, do not copy Draft companion trees or invent relation policy.

### Definition of Done

Focused synthetic-project checks and independent review verify the stated behavior without live MCP tests, deployment, migration, or held-batch replay. Review dependent next Task before acceptance execution.

### Verified execution checkpoint

Done-to-Active canonical placement with existing child preservation and exact predecessor archive passed, as did moved-publication cleanup-failure and native postwrite exact rollback checks. Independent review confirmed moved-path recovery has the expected published-bundle guard. Separate same-path concurrent-edit protection is retained under P2475; parent P2469 remains Active.
