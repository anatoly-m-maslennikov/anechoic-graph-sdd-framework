---
atom_family: SPEC
atom_id: AN-S-1343
container:
  component: C15
tier: 5
context:
  lens: DevOps
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T22:43:29.899404+00:00"
---
## Summary
Deliver shared diagnostic record carriers

## Claim

### Prose Claim

PROGRAMMATIC operational diagnostics **must** use **`=1`** shared structured record representation at their declared diagnostic output boundary.

- Use the record fields, severity, and sanitization rules in AN-S-4741 and AN-S-1902. Include deployment, request, job, Workflow, domain state, attempt and exception class when applicable and available.
- canonical action **or** Event references are carried unchanged **when** available; absent references remain absent rather than being invented for an exporter.
- a concise human rendering **and** **any** exporter-specific encoding are derived representations of that record, **not** separately maintained diagnostic facts **or** schemas with competing meanings.
- Write Studio technical records to stderr under AN-S-4741. Keep business Event Records in their declared Journal.
