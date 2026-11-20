---
identity:
  atom_id: AN-S-3116
context:
  container:
    component: C45
  tier: 1
  lens: DES
  template: DECISION
state:
  status: active
  version: 1
  updated_at: '2026-11-20T16:34:57.901983+00:00'
relations:
  REFERENCES:
  - AN-S-2565
  - AN-S-348
---
## Summary

Store native Workbench DuckDB data on disk

## Claim

### Prose Claim

- Use one Project-local DuckDB file and the existing serialized owner.
- Keep the database and spill files in Workbench runtime state.
- Keep Project sources and the Journal authoritative for their facts.
- Validate retained data before serving queries.
- Reuse valid parsed imports and reconcile changes made while Workbench was stopped.
- Store live results in the database. Apply expiry, pinning, and startup rules.
- Rebuild one table or all tables on demand. Include dependent tables by default.
- Publish new result IDs with their View bindings and pins.
- Report rebuild failures to stderr and the requesting HTTP or MCP client.
- Roll back failed SQL writes.
- Require an explicit restart if a failure may have invalidated graph registration.
- Make a second writer exit with an explicit lock error.
