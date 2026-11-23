---
atom_family: TKT
atom_id: AN-T-1496
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 2
  updated_at: 2026-10-05 02:47:17 +0000
---
## Summary

Implement Release Version from reviewed RMED

# Summary

Implement Release Version from reviewed RMED

## Objective

Within <=15 minutes per bounded implementation slice, implement the independently accepted Release Version contract using existing components.

## Details

Own only the release capability implementation/tests and necessary additive discovery/MCP/orchestrator bindings. Begin with golden E2E tests and mocks for complete copy/compile/test/install/Skill/image flow and non-happy cases. Preserve current fifteen-route contracts unless reviewed source explicitly extends them. Bind full package Version/digests and enforce source/settings/Journal preservation, rollback and no old-image deletion before successful new installation/image verification. Do not provision around C449, retry C447, publish images, deploy or force-remove shared images. Decompose into <=15-minute slices before work exceeding the bound.

### Bounded decomposition

CA-P-1639 owns pure sealed contracts; CA-P-1640 owns the independent golden corpus; CA-P-1641 owns non-active complete package staging; CA-P-1642 binds the candidate compiler interface. These independent leaves can run in parallel with separate file ownership. All four block CA-P-1643 integration and additive admission; CA-P-1644 independently reviews resulting evidence. Parent remains Active until its full requested implementation is complete. Split any leaf exceeding15 minutes; no source, pure model, mock, development worker or build substitutes for P1624 actual image gates.

## Definition of Done

Reviewed source is implemented with focused passing golden tests, source-current bindings, truthful shared Run outputs and exact implementation diff. Mock/development proof is labeled separately from actual install/Docker proof.
