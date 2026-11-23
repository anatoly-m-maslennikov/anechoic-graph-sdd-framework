---
atom_family: SPEC
atom_id: AN-S-3582
container:
  component: C20
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 12
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

manage the runtime **with** Docker Compose

# Summary

manage the runtime **with** Docker Compose

## Scope

the Docker runtime's implementation **and** lifecycle management.

## Claim

implement runtime management through Docker Compose using **=1** image **and** separate MCP, worker **and** Agent services with explicit persistent-state boundaries.

## Details

1. build from admitted Engine sources **and** pinned runtime dependencies; exclude Project data, credentials **and** generated state from the build context.
2. use non-root services, a read-only image filesystem **and** **only** the mounts required by their responsibilities.
3. give the worker a separate Docker scheduler namespace. keep the shared Journal **and** report locations unchanged.
4. publish Docker routing **only** **after** worker readiness. queue calls **must** fail visibly **if** the selected runtime is unavailable; they **must not** fall back **to** another queue.
5. preserve saved dispatch evidence across restart. after uncertain dispatch, require reconciliation rather than another Agent call.
6. keep automatic restart disabled. provide explicit restart **and** a stdio MCP launcher; lifecycle commands do **not** create Workflow requests.
