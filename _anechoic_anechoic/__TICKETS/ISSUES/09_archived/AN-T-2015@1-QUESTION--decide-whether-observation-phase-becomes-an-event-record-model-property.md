---
atom_family: TKT
atom_id: AN-T-2015
container:
  component: C9
priority: 2
context:
  template: question
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Decide whether Observation Phase becomes an Event Record model Property

## Question

Should the legacy Work Journal execution-observation labels (Started, Progressed, Completed, Failed, Interrupted, Abandoned, Recovered) later become an explicitly declared Event Record model Property, distinct from the accepted business Action values such as `create` and `update`?

## Why this is non-blocking

CA-R-1643 preserves the legacy labels only in serialized Journal Carrier Main Content. No new Event Record Property or business-action value is required to adopt this candidate packet.
