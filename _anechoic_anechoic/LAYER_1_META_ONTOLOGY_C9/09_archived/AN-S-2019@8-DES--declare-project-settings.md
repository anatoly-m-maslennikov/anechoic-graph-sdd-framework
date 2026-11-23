---
atom_family: SPEC
atom_id: AN-S-2019
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 8
  updated_at: 2026-11-02 16:48:11 +0400
---
## Summary

Declare Project.Settings

## Claim

### Formal Claim

```CFEL
# model
Project.Settings{::1}:: []{::0};

Project.Settings.*[in (Name, Prefix, AI Agent Confidence Threshold, Artifact Timestamp Timezone, Code-Root Locators, Confidence, Framework Control-Root Locator, Interaction, Authority Modes, Implementation Retry Limit, RMED Review)]{::3..11}
```

