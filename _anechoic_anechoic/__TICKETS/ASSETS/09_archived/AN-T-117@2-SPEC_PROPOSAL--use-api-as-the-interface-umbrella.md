---
atom_family: TKT
atom_id: AN-T-117
container:
  component: C00
priority: 2
context:
  template: spec_proposal
state:
  status: archived
  version: 2
  updated_at: 2026-10-29 21:51:04 +0400
---
## Summary

Use API as the interface umbrella

# Summary

Use API as the interface umbrella

## Decision

API is enough as the umbrella for a Package invocation interface. API forms can include CLI, Web API/REST API, RPC and others. Do not treat API and CLI as two peer categories, or create separate primary branches for every example now. Some Packages expose a public API; API exposure is not mandatory for every Package. Public here concerns the exposed Package boundary, without implying Internet deployment.

## State

Model/Definition preparation only. Current methodology, Engine code and runtime are unchanged.
