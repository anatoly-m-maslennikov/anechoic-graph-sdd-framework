---
atom_family: TKT
atom_id: AN-T-1591
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 08:16:43 +0400
---
## Summary

Check authenticated readiness **and** return MCP results

# Summary

Check authenticated readiness **and** return MCP results

## Objective

the AI Agent implements the launcher's authenticated readiness gate **and** safe result construction.

## Details

- input: the startup result, result RMED, **and** startup/output golden tests.
- output: a bounded host-side readiness check using the accepted credential source **and** verified published endpoint; ready output includes the actual `/mcp` URL **and** safe instance metadata, while failures expose no success URL.
- verification: exercise correct/wrong/missing credentials, timeout, hostile Host/Origin, unhealthy service, **and** output redaction. an MCP handshake is required **only if** the reviewed readiness contract selects it.
- effort: **`<=15`** minutes for **`=1`** AI Agent; the Epic's decomposition rule applies **before** execution **if** the estimate no longer holds.

### Definition of Done

- completion evidence: all 12 startup test methods passed, covering the 13 safe condition codes, authenticated readiness, failure attribution, metadata **and** token redaction; the default backend uses a bounded host MCP initialization exchange.

the Plan is **not** Done **if** ((a success result precedes the required readiness evidence) **or** (credentials appear **in** URLs, ordinary results, **or** diagnostics) **or** (the readiness/output tests fail)).
