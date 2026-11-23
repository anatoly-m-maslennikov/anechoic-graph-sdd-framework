---
atom_family: SPEC
atom_id: AN-S-1894
container:
  component: C00
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 10
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Verify one ANECHOIC-aligned FPF Extension revision

# Verify one ANECHOIC-aligned FPF Extension revision

## Claim checked

CA-M-290 produces one immutable project-local FPF Extension revision that is ANECHOIC-aligned, directly invokable, correctly persistent, asynchronously safe, **and** separately installable **and** activatable.

## Applicable when

Apply **before** publishing, installing, activating, updating, downgrading, **or** reloading **any** FPF Extension revision.

## Test case

Materialize the same pinned upstream revision **and** ordered overlay twice; install one result **without** activation; **then** activate it separately **and**, **in** fresh Codex sessions, exercise direct `$fpf` routing, one persistent analysis, one explicit Question Concern request, one ordinary non-persistent question, one Hook-triggered deferred action, one hung Tool, one hung MCP request, one hung worker, independent recovery `status`, `stop`, `start`, **and** `reload`, automatic retry-budget exhaustion, restart recovery, **and** rollback **to** the prior selected revision.

## Acceptance criteria

Both builds have identical manifests, inventories, **and** digests. Installation changes no applicable methodology **and** mutates neither upstream nor user-global FPF sources. Activation selects exactly the installed revision. Direct `$fpf` needs no `ca` wrapper. The Analysis Report is a valid `CA-A` Carrier **in** the correct narrowest `02_analysis/`; the explicit Concern is a valid one-Claim `CA-C` Carrier **in** the correct `01_concern/`; the ordinary question persists nothing. Hook acknowledgement returns within its declared bound **without** waiting for worker work. Manual recovery controls remain bounded **and** responsive while the Hook, Tool, MCP request, manager, **or** worker is hung; the automatic supervisor performs no domain effect; accepted work survives stop, reload, **and** restart **without** duplicate effects; **and** exhausted automatic recovery opens a visible circuit. Rollback restores the exact prior selection **and** installed state.

## Failure disposition

Reject the Extension revision **and** preserve the sealed source frontier, manifests, inventories, digests, installation **and** activation receipts, fresh-session discovery evidence, generated Atom diagnostics, Hook latency, queue **and** worker traces, lifecycle actions, circuit state, **and** rollback evidence.
