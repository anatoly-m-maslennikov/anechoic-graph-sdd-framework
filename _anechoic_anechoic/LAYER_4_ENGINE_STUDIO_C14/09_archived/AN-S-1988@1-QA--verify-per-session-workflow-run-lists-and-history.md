---
atom_family: SPEC
atom_id: AN-S-1988
container:
  component: C14
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Verify per-session Workflow Run lists and history

## Claim

### Prose Claim

Exercise the generic session contract through two client-adapter fixtures without harness/provider branches in the runtime. Create Runs for two client sessions in one Project and one session in another Project. Each default session read must select only its own Project/session association.

Complete a Run, reconnect its session, and check that it leaves the active list while its recorded history remains associated with that Run. History reads must not resume an ended Run, repeat an effect or append invented events. Query-result expiry and query-log cleanup must not erase Run history. Missing or mismatched bindings must not select another session. Use the existing executor’s state transitions and history retention rules.
