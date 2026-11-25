---
atom_family: TKT
atom_id: AN-T-3490
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-24T10:31:52.059608+00:00'
---
## Summary

Generate TypeScript from the admitted eDSL Model

## Work

Generate public TypeScript types and validators, where expressible, from the exact resolved admitted Model. The Python eDSL remains the only Model fact source. Use zero magic and report constraints that TypeScript cannot express rather than silently dropping them.

Integrate a real frontend consumer and preserve Model fingerprint parity for Project custom Models across the generated TypeScript and the admitted Model. Keep this work as a separate follow-up branch.

## Acceptance

A real frontend consumer uses generated public types and applicable validators. A Project custom Model produces matching fingerprints for the admitted Model and generated TypeScript. Missing, stale, or mismatched outputs fail explicitly, and unsupported constraints are reported.
