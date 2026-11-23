---
atom_family: TKT
atom_id: AN-T-252
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-10-10 18:08:27 +0400
---
## Summary

Protect existing state during installation migration

# Summary

Protect existing state during installation migration

## Objective

the AI Agent supplies a verified migration that preserves existing operational state while `.anechoic_install` becomes the beta package boundary.

## Details

- scope: the installation/release contribution of the ANECHOIC Framework Instance delivered by the anechoic Project.
- input: existing `.anechoic_install/project_mcp`, `mcp_hot_reload`, `workflow_orchestrator` **and** related databases, locks, receipts, history **and** pending work.
- first repair `INSTALL_TOOLS/install_tools.py` whole-directory legacy deletion; installer execution **must not** remove live state, historical evidence, credentials **or** unrelated contents. use explicit owned-path admission rather than a directory sweep.
- implement **and** test quiescing, exact source/target inventories, migration into selected-Project `.anechoic_runtime`, state-reader/selector updates, resumability **and** rollback. preserve Journal records **and** historical references; interrupted Runs remain honestly recorded, **not** passed **or** automatically replayed.
- stage the migration **and** exercise it **only** against disposable fixtures during preparation. actual Project state moves occur **in** the local release Workflow **after** its full-suite gate passes.
- unmapped **or** protected contents need an explicit retention/disposition decision. test initial failure, interrupted migration, repeated invocation, current-state recovery **and** preservation of another Project.
- effort: own work for **=1** AI Agent **must** fit **<=15** minutes. **if** this Plan needs larger own work, decompose it **before** execution **and** preserve its Objective **and** acceptance.
- control: use applicable Operator input **and** inherited Framework Instance Settings for permission, confidence **and** retry gates. creation is planned work **only**, **not** permission to execute the local/public cycle immediately.

### Definition of Done

the Plan is **not** Done **if** legacy installation can delete operational state, an existing record is lost **or** rewritten as successful, migration cannot resume/rollback, **or** live cutover occurs **before** the local release gate.
