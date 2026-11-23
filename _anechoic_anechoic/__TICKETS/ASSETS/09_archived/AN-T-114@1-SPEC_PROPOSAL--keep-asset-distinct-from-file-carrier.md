---
atom_family: TKT
atom_id: AN-T-114
container:
  component: C00
priority: 2
context:
  template: spec_proposal
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 00:13:17 +0400
---
## Summary

Keep Asset distinct from File Carrier

# Summary

Keep Asset distinct from File Carrier

## Decision

Use Package > Asset, not Asset File. Asset is the logical, non-executable Implementation content needed by runtime or tests. Files are Carriers representing that content; being carried in a file does not make File part of the logical-kind name.

This overrides the Asset File naming decision in CA-A-1270. Keep the Runtime Package/Test Package specializations, common Module and Asset kinds, separate Documentation, and the Model root unchanged. It introduces no alias, new usage field, representation-count rule or runtime behavior.

## State

Restore the prepared Asset Definition as the promotion candidate. Keep the Asset File Draft only as explicitly superseded history. Current methodology and historical review reports remain unchanged.
