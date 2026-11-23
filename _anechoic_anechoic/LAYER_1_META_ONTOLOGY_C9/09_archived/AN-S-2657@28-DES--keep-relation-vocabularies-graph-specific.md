---
atom_family: SPEC
atom_id: AN-S-2657
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 28
  updated_at: 2026-10-29 07:45:26 +0400
---
## Summary

Keep relation vocabularies graph-specific

## Claim scope

Relation Types, their shared Project identities, and any applicable Graph Rule constraints in ANECHOIC Graphs.

## Claim

Relation Type names are shared across ANECHOIC Graphs and unique within the Project. A Relation Type is not owned by a graph kind. Existing Graph Rules, where applicable, supply graph-specific endpoint classes, endpoint graph contexts, cardinality, permissions, and prohibitions for that shared Type. They do not create graph-owned Type copies or impose a new per-Type/per-graph admission registry; this contract chooses neither default allow nor default deny.

instances of the same graph kind governed by the same Applicable Methodology **must** reuse the same defining Relation Type authority and any applicable Graph Rules. Matching names identify the shared Type; they do not create interchangeable copies or erase graph-specific constraints.

where a Graph Rule applies, it determines graph-specific endpoint constraints, **not** a requirement that all endpoints occupy the same graph. admitted cross-graph endpoints and source references under CA-R-1472 retain their endpoint identity and source traceability. another graph **may** represent a source-traceable reference **or** view of the Relation **without** creating a graph-specific Type copy.
## Details
