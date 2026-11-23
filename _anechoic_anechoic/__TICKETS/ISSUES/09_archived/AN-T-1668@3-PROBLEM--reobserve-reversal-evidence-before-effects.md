---
atom_family: TKT
atom_id: AN-T-1668
container:
  component: C16
priority: 2
context:
  template: problem
state:
  status: archived
  version: 3
  updated_at: 2026-10-23 03:06:32 +0400
---
## Summary

Reobserve reversal evidence before effects

# Summary

Reobserve reversal evidence before effects

## Concern

The native Revert provider treats equality with a frozen request as currentness without re-reading its referenced permission, approval and history evidence.

## Evidences

P1566's read-only reproduction changed a referenced permission record from granted to revoked and changed its bytes/hash. provider.revalidate(original_request) still returned an empty mismatch list. No effect, Run, Journal event or target mutation was invoked. R1833/E553/E554 require stale or revoked bindings to block before effects.

## Blast radius

Native Revert admission and later effects cannot be accepted on this evidence. P1568 repairs the bounded defect; P1567/W10 and final image acceptance retain this gate. Independent query and other route preparation continue.

## Resolution

Accepted D536@2 and P1574 implement actual bounded evidence reobservation at admission, pre-start and every effect. Actual recorded Operator approval binds complete ordered payloads; executor and capability permission revocation stop remaining effects. Independent P1581 accepted the saved provider, with 24/24 Revert tests and registered native selected Revert proof passing. The recorded currentness defect is resolved; complete W10/shared-recording, queue/MCP and immutable-image gates remain separately required and are not implied by this Concern's resolution.
