---
atom_family: TKT
atom_id: AN-T-3463
container:
  component: C00
priority: 2
context:
  template: task
  label: Epic
state:
  status: active
  version: 1
  updated_at: '2026-11-23T11:50:07.779751+00:00'
---

## Summary

Move dbt-style data pipelines into DuckDB

## Outcome

DuckDB runs the relational transformations for admitted Project data.
Kernel admission refreshes affected keys in the same transaction.

## Tasks

- [x] Inventory pipelines. The Project uses dbt naming and DuckDB execution.
- [x] Publish Atom rows and references from a typed batch. Derive affected graph edges and vertices in SQL.
- [x] Batch Spec metrics and bindings. Preserve full and incremental parity and public query results.
- [x] Reuse filtered Workbench results for page rows and totals. Use one status scan per schema table.
- [x] Profile narrower lifecycle SQL. The tested shape was slower on 50,000 synthetic Atoms.
- [ ] Profile actual lifecycle workloads before changing the selector or adding indexes or stored maxima.

## Decisions

AN-S-4449 gives the general SWD rule. AN-S-4450 defines the DuckDB implementation under SWD/DBT. AN-S-3401 defines table roles.
