---
atom_family: SPEC
atom_id: AN-S-1779
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 24
  updated_at: 2026-10-29 10:13:51 +0400
---
## Summary

Serialize explicit Plan Assignees

## Claim scope

explicit Plan Assignee overrides in Plan File Carriers.

## Claim

a Plan File Carrier **may** serialize **`=1`** explicit Assignee override as top-level frontmatter `assignee`; omission **must** preserve CA-R-1585-CORE_META_MODEL-RULE--default-plan-work-assignment-to-an-ai-agent for its own work rather than copying the default.
