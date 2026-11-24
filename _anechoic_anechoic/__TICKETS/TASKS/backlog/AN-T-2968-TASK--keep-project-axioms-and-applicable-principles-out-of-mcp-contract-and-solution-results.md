---
atom_family: TKT
atom_id: AN-T-2968
container:
  component: C21
priority: 2
context:
  template: task
  label: Task
state:
  status: backlog
  version: 1
  updated_at: "2026-11-21T20:10:17.217577+00:00"
---
## Summary

Keep Project Axioms and Applicable Principles out of MCP contract and solution results

## Details

Run `query_template` with `component: "C00"`. `fetch_contracts` includes Project Axioms `AN-S-1428@1` and `AN-S-1429@1` and Component Manifests such as `AN-S-3038@1`. `fetch_solutions` includes the Project Applicable Principle `AN-S-3190@1`. These results mislead callers that use the templates to retrieve Project Contracts or Solutions.

Coordinate with `AN-T-2932`, which owns admission of the Project Atom roles and tiers. This ticket tracks the MCP query behavior and its regression checks.

## Acceptance Criteria

- `fetch_contracts` for C00 returns Project Contracts and excludes Project Axioms and Project and Component Manifests.
- `fetch_solutions` for C00 excludes Project Applicable Principles.
- Regression checks cover the reported cases and confirm that Component calls still retrieve their intended Component Contracts and Solutions.
