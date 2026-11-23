---
atom_family: TKT
atom_id: AN-T-2085
container:
  atom: AN-T-2078
priority: 2
context:
  template: task
state:
  status: archived
  version: 4
  updated_at: 2026-11-11 06:55:00 +0400
---

## Summary

Verify Engine performance and resource regressions

## Objective

Run the existing latency, 500-Atom throughput, cold rebuild and resource/soak acceptance against the final combined code revision after all performance-affecting changes. Record that revision and rerun affected acceptance if it changes before delivery. Preserve current acceptance limits and report CPU peak caveats separately. Do not substitute profiling runs for acceptance.

## Subtasks

- [x] Review and fix the next scoped input batch. (ETA: up to 15 min.)
- [ ] Complete one scoped implementation or verification batch; split before exceeding 20 min.
- [ ] Review and fix the result; record a small P / Work Report. (ETA: up to 15 min.)

## Definition of Done

The stated work has actual source/code/test evidence. Every unresolved or unrun case is explicit; no Task text replaces RMED.

## Candidate acceptance

The nine Docker tests passed on d520960c81eb, including the short resource guard. The 1,800-second soak is running on that image. The Docker evidence and running-process receipt are under `.anechoic_tmp/CA-P-2791/CA-P-2817/`.
