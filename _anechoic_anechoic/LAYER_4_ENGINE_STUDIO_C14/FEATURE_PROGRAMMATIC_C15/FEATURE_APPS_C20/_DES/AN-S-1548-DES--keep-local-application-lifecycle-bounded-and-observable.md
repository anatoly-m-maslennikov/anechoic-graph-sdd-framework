---
atom_family: SPEC
atom_id: AN-S-1548
container:
  component: C20
tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary
Keep local application lifecycle bounded and observable

## Claim

### Prose Claim

an admitted local App service **must** expose supervised, bounded, **and** observable startup, shutdown, restart, cancellation, timeout, **and** recovery outcomes for its owned background work.

- the Operator **or** admitted client can distinguish starting, running, stopping, completed, failed, **and** unresolved recovery outcomes **without** inferring success from a disconnected session **or** stopped process.
- interrupted work remains subject **to** that application's declared recovery boundary; restarting the service **must not** silently lose work, duplicate effects, **or** promote transient state **to** MODEL//ANECHOIC <+ Project authority.
- unsupported lifecycle capabilities remain explicit rather than being reported as performed. WORKFLOW_ORCHESTRATOR retains its narrower accepted-work **and** handoff rules within its own declared boundary.

this Requirement selects no supervisor implementation, uniform retry policy, permanent server, **or** Workflow for building the application.
