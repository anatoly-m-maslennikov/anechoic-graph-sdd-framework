---
atom_family: TKT
atom_id: AN-T-4030
container:
  component: C00
priority: 2
context:
  template: task
  label: Epic
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-26T21:41:33Z"
---
## Summary

Measure Agent Maintenance Before and After Refactoring

## Objective

Measure whether agents solve the same small maintenance tasks more
reliably or with less effort on the current code than on the code
before refactoring.

## Scope

Run 15 matched tasks on two frozen versions. Each trial uses a fresh
agent with no memory or tools. The agent submits a patch from a supplied
source bundle. A separate runner checks the patch against hidden tests.

## Tasks

1. AN-T-4031 freezes the revisions, prompts, and acceptance tests.
2. AN-T-4032 runs the 30 isolated trials.
3. AN-T-4033 grades the patches and reports the paired results.

## Done when

Every task has a result on both revisions. The report compares pass
rate, tokens, and wall time. Failed trials count toward effort.
The report attributes the result to the combined refactoring.
