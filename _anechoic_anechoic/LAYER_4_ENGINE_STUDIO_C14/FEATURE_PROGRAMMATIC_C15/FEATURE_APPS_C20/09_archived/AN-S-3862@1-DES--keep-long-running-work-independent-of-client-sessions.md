---
atom_family: SPEC
atom_id: AN-S-3862
container:
  component: C20
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-09-18 21:23:47 +0000
---
## Summary

Keep long-running work independent of client sessions

# Keep long-running work independent of client sessions

WORKFLOW_ORCHESTRATOR **must** keep accepted work independent of the lifetime of the client session that submitted it.

- submission returns an identifier for accepted work **without** waiting for the Workflow **or** a long-running Action **to** finish.
- the Operator **or** an authorized client can inspect progress, results, failures, **and** pending decisions; supply requested input; request cancellation; **and** reconnect **to** the same accepted work.
- acceptance, a cancellation request, **and** actual completion are distinct outcomes. disconnecting a client **must not** silently cancel work **or** make unfinished work appear successful.
- waiting for an Action **or** Operator input **must not** prevent the application from reporting state **or** accepting admitted control requests.
- asynchronous submission does **not** itself authorize parallel Actions, concurrent mutation of an Artifact, **or** execution outside the applicable permissions.

the result **must** disclose an unsupported control **or** execution capability rather than imply it was performed.
