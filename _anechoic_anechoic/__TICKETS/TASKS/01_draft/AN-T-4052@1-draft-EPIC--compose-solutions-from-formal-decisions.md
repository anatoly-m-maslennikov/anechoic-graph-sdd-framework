---
atom_family: TKT
atom_id: AN-T-4052
container:
  component: C75
priority: 2
context:
  template: task
  label: Epic
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T09:13:09.606849+00:00'
---
## Summary

Compose Solutions from formal Decisions

## Objective

Let a Component Solution use formal Decisions as named modules. Keep each
Decision under the owning Component and give it one rule or design choice.

## Work

- Define the formal Decision and how a Solution references its exact revision.
- Check each Decision in Lean, then check the assembled Solution against the
  Component Manifest. Report missing or conflicting Decisions with source pins.
- Pilot this in C88. A Decision defines fact equality and missing-value
  verdicts. The Solution specifies when to run the three comparisons.

## Acceptance

The C88 Solution uses one pinned Decision. Lean checks the Decision and the
assembled Solution. A missing, stale, or conflicting Decision prevents a
passing result.
