---
atom_family: SPEC
atom_id: AN-S-1343
container:
  component: C15
tier: 5
context:
  lens: DevOps
state:
  status: active
  version: 1
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary
Deliver shared diagnostic record carriers

## Claim

### Prose Claim

PROGRAMMATIC operational diagnostics **must** use **`=1`** shared structured record representation at their declared diagnostic output boundary.

- the delivered record schema represents the context required by CA-M-414 **and** the applicable production fields under CA-D-396. it preserves the severity **and** safety rules of ANECHOIC-GOV-REQU-315 **without** defining another field meaning **or** severity vocabulary.
- canonical action **or** Event references are carried unchanged **when** available; absent references remain absent rather than being invented for an exporter.
- a concise human rendering **and** **any** exporter-specific encoding are derived representations of that record, **not** separately maintained diagnostic facts **or** schemas with competing meanings.
- production record placement follows the declared Logging Policy sink. the Project Journal is **not** an alternative diagnostic output Carrier.
