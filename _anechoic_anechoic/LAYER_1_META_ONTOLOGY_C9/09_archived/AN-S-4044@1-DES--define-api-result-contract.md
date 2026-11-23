---
atom_family: SPEC
atom_id: AN-S-4044
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

Define API Result Contract

## Claim

An API Result Contract defines the expected format and meaning of results for an API operation. It describes what callers can expect under its applicable conditions, rather than the data produced by a particular execution.

## Semantics

The operation-specific contract may describe returned values, errors or effect summaries. This Definition prescribes no common envelope or mandatory field set across all APIs. API Self Documentation can expose the contract, while Execution.Result supplies an actual result to assess against it.

## Details

CA-A-1276 records the Operator decision. Numeric identity, property formats/counts and Current adoption remain pending; this does not implement a result envelope or Journal writer.
