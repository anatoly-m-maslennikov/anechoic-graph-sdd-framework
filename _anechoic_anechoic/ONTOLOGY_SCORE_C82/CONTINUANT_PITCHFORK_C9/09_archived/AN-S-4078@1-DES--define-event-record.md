---
atom_family: SPEC
atom_id: AN-S-4078
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 07:32:39 +0400
---
## Summary

Define Event Record

## Claim

An Event Record is a persistent record within exactly one Journal that describes something that happened. It can RECORD an actual occurrence, including a Workflow Run. The record is not the occurrence itself. It can preserve or describe an actual Execution.Result.

### Formal claim

```text
Journal > Event Record
Event Record ((RECORDS)) Workflow Run
```

## Semantics

The Workflow Run edge is the requested model case, not a declaration that all records must describe Workflow Runs. The Journal contains the record; it does not contain the actual occurrence. A record's Carrier represents that record, not the living execution. IS_RECORDED_BY is the derived opposite view of RECORDS, not another stored fact.

## Details


CA-A-1276 distinguishes the recorded result from the execution and from its API contract; it adds no mandatory result field or recording obligation.
