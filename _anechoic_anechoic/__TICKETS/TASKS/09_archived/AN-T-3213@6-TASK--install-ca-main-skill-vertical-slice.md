---
atom_family: TKT
atom_id: AN-T-3213
container:
  component: C00
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 6
  updated_at: 2026-10-25 01:31:47 +0400
---
## Summary

Install CA Main Skill Vertical Slice

# Install CA Main Skill Vertical Slice

**when** CA-P-940 is Done, **then** the Assignee **must** install one versioned CA vertical slice containing the accepted authority snapshot, runtime Tools, MCP surface, canonical Skill, and the Codex host adapter.

## Scope

`((accepted source Carriers from CA-P-936 through CA-P-940) union (content-addressed release, installation manifest, launchers, service definitions, Codex host registrations, digests, receipts, rollback boundary, and installation checks))`

## Definition of Done

the Task is **not done if** (installation mutates outside the authorized boundary, includes uncommitted or unvalidated source, changes unrelated Hooks or host configuration, lacks exact source and installed digests, cannot be rolled back, leaves mixed release versions, or bypasses the installed-execution guard **or** manual and automatic lifecycle controls are not reachable from the installed runtime **or** Codex does not discover the intended host adapter **or** installation proof is reported as runtime proof **or** clean-install and upgrade checks fail).

## Details

publish and activate one immutable release within the host-support boundary established by CA-P-936. Claude installation is outside this Task. keep source validation, installation result, process state, and runtime behavior as separate evidence classes. preserve existing disabled Hook state unless the accepted authority and explicit installation boundary require a bounded trigger adapter.
