---
atom_family: SPEC
atom_id: AN-S-1779
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 27
  updated_at: "2026-11-25T23:09:47.608590+00:00"
---
## Summary

Serialize explicit Plan Assignees

## Claim

### Prose Claim


explicit Plan Assignee overrides in Plan File Carriers.


Where the model admits an explicit Assignee override, a Plan File Carrier serializes **`=1`** such value at its declared Header path through the common name encoding; omission **must** preserve CA-R-1585-CORE_META_MODEL-RULE--default-plan-work-assignment-to-an-ai-agent for its own work rather than copying the default.
