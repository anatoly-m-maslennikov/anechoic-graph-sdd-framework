---
atom_family: SPEC
atom_id: AN-S-1414
container:
  component: C21
tier: 5
context:
  lens: DevOps
state:
  status: active
  version: 18
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Deliver the same-port MCP health browser view

## Claim

### Prose Claim

Deliver the health browser view at /anechoic/health on the same configured loopback-published MCP listener, preserving its machine JSON representation and status semantics. Deliver the implementation and safe fixed error labels with the existing MCP package/image and operational instructions, not as an independent server, frontend build or execution-history authority.

## Details

### Scope

Delivery representation of the bounded health view in the existing MCP HTTP service.

- Keep native implementation in the declared MCP delivery place and existing package/image boundary; add no port, credentials, service lifecycle or Tool registry.
- Explicit text/html renders gateway/registry observations, recent Tool calls and recent Workflow observations with timestamps, outcome/status, separate scheduler/actual Workflow fields and safe error labels.
- Default/application-json/wildcard serves health JSON with one readiness field, `state`. Callers check `state == 'ready'` for readiness.
- Apply AN-S-4803. Return HTTP 200 with `state: pending` during live startup or replay. Return HTTP 200 with `state: degraded` when health can report a known Project input problem that prevents readiness or limits service. Preserve error statuses for genuine service failures and Host or Origin rejection.
- State process-local since-start and bounded history; absent/unobserved is unknown. Health GET/snapshot dispatches no operations. Only CA-R-2782’s explicit Workbench-restart POST is allowed, through the same native MCP operation; add no replay, reload or mutation control.
- Document the configured existing host port, never a developer-specific port. Normal local release delivers the changed package/image only after complete gates; source pages, snapshots, screenshots or builds are not installed-adoption evidence.
