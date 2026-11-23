---
atom_family: SPEC
atom_id: AN-S-4406
container:
  component: C20
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 20
  updated_at: 2026-11-10 09:54:52 +0400
---
## Summary

Verify the APPS Scope Unit topology

## Claim

### Prose Claim

#### Claim checked

CA-M-196 registers the three immediate unordered APPS units with distinct responsibilities **and** without project authority.

#### Applicable when

Apply whenever an immediate APPS child's ownership, structural identity, responsibility boundary, **or** realization path changes.

#### Test case

Examine the current active APPS authority and its child declarations, using derived representations only as supporting evidence. Exercise graph access once with `GRAPH_UI` absent.

#### Acceptance criteria

`WORKBENCH`, `GRAPH_UI`, **and** `AGENT_HOST_PLUGINS` are distinct immediate unordered APPS children. `WORKBENCH` operates headlessly for Tools **and** MCP; `GRAPH_UI` remains optional; **and** no child becomes project authority.

#### Failure disposition

Reject the topology and preserve the examined authority, supporting evidence, **and** every missing, duplicate, dependent, **or** conflicting boundary.
