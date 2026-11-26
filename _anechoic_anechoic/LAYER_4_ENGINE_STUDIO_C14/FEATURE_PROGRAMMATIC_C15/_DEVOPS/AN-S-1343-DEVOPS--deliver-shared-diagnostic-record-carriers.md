---
atom_family: SPEC
atom_id: AN-S-1343
container:
  component: C15
tier: 5
context:
  lens: DevOps
state:
  status: "active"
  version: 3
  updated_at: "2026-11-25T22:43:29.983346+00:00"
---
## Summary
Deliver shared diagnostic record carriers

## Claim

### Prose Claim

PROGRAMMATIC operational diagnostics **must** use **`=1`** shared structured record representation at their declared diagnostic output boundary.

- Use the record fields, severity, and sanitization rules in AN-S-4741 and AN-S-1902. Include a concise message. When applicable and available, include deployment environment and version, request, job, Workflow, domain entity and state, attempt, and exception class.
- canonical action **or** Event references are carried unchanged **when** available; absent references remain absent rather than being invented for an exporter.
- a concise human rendering **and** **any** exporter-specific encoding are derived representations of that record, **not** separately maintained diagnostic facts **or** schemas with competing meanings.
- Write Studio technical records to stderr under AN-S-4741. Keep business Event Records in their declared Journal.
