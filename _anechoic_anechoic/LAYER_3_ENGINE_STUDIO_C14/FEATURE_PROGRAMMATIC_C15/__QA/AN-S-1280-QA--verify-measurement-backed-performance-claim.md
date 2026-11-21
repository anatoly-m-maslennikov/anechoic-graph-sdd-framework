---
atom_family: SPEC
atom_id: AN-S-1280
structure:
  container:
    component: C15
  tier: 5
context:
  lens: QA
state:
  status: active
  version: 24
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify measurement-backed performance claim

## Claim



### Prose Claim
#### Claim checked

one PROGRAMMATIC performance claim is supported by a representative workload,
preserved baseline, observed distribution, **and** comparable observation.

#### Applicable conditions

apply **when** a component proposes **or** assesses a performance-sensitive change.
no numerical budget is implied **where** no bounded owner has admitted one.

#### Test case

evaluate one claimed performance change against its selected surface **and**
recorded baseline.

#### Acceptance criteria

pass **only** **when** the workload input, environment, baseline, observed
distribution, **and** comparison threshold are recoverable **and** support the stated
claim.

#### Failure disposition

reject the performance claim **without** a representative baseline; do **not** invent
a numeric budget.

#### Sources

- [CA-M-416 — Measure before optimizing PROGRAMMATIC performance](../05_method/CA-M-416-PROGRAMMATIC-STANDARD-ENG_POLICY--measure-before-optimizing-programmatic-performance.md)
