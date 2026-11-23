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
  version: 15
  updated_at: 2026-10-24 09:42:52 +0400
---
## Summary

Serialize explicit Plan Assignees

# Summary

Serialize explicit Plan Assignees

## Scope

explicit Plan Assignee overrides in Plan File Carriers.

## Claim

a Plan File Carrier **may** serialize **`=1`** explicit Assignee override as top-level frontmatter `assignee`; omission **must** preserve CA-R-1585-CORE_META_MODEL-GENERAL-REQUIREMENT--default-plan-work-assignment-to-an-ai-agent for its own work rather than copying the default.

## Details
