---
atom_family: SPEC
atom_id: AN-S-3864
container:
  component: C20
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 13
  updated_at: 2026-10-27 19:59:41 +0400
---
## Summary

Separate Workflow coordination from Action execution

# Separate Workflow coordination from Action execution

**to** implement WORKFLOW_ORCHESTRATOR, separate responsive coordination from long-running Action execution.

- use an on-demand local background service for coordination. an HTTP server, remote deployment, **or** graphical interface is **not** required by this Method.
- execute long-running **or** blocking Actions through bounded workers **or** subprocesses; waiting for external results **or** Operator input **must not** block the coordination interface.
- keep Workflow selection, transition, handoff, retry, **and** approval behavior driven by applicable methodology inputs rather than independently authored application branches.
- use stable request, Run, **and** dispatch identities with durable handoff recording, duplicate suppression, **and** the declared effect-safety mechanism. separate transient worker state from canonical Journal history **and** rebuildable views.
- keep client transport **and** worker adapters replaceable. select concrete libraries, wire formats, persistence Carriers, **and** resource limits through their applicable authority rather than assuming an unapproved default.

asynchronous coordination does **not** require **every** Action implementation **to** use asynchronous programming **or** execute concurrently. this Method does **not** install hooks **or** migrate the existing commit-automation service.
