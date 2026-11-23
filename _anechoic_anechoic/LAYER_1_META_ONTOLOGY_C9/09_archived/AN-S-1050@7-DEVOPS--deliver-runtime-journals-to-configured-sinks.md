---
atom_family: SPEC
atom_id: AN-S-1050
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Deliver runtime Journals to configured sinks

# Summary

Deliver runtime Journals to configured sinks

## Scope

technical and business runtime Journal Carriers.

## Claim

runtime technical **and** business Journals **may** be delivered **to** an explicitly configured local database, remote database, **or** governed logging sink. these Carriers **need not** reside under `.anechoic_<project_name>/_journal/` **or** `.anechoic_runtime/`.

## Details

Journal classification and recorded-history authority are independent of storage technology. The configuration identifies the intended sink; applicable production logging policy remains in force. The shared Project-control Work Journal and persistent view Projections retain their separate _journal and _projection locations. Runtime cleanup and sink migration must preserve accepted Journal history; this Delivery does not authorize history deletion or change retention policy.
