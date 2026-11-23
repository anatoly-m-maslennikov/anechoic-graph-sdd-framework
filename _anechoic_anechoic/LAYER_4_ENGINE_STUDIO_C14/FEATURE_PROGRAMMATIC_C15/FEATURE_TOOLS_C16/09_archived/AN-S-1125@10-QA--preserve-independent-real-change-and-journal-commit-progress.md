---
atom_family: SPEC
atom_id: AN-S-1125
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 10
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Preserve independent real-change and Journal commit progress

# Preserve independent real-change and Journal commit progress

## Test case

delay Journal append while a valid real-change action reaches the Git gate, **then** delay the real-change commit while Journal append completes. batch the completed Journal record later, including a batch on the configured periodic interval.

## Acceptance criteria

neither branch gates the other's non-conflicting progress. the real-change commit **contains** **only** its sealed targets; Journal append remains independently durable; the later Journal-only commit **contains** **only** selected Journal Carriers; **and** both commit effects remain serialized by one repository gate **without** losing their common action provenance.
