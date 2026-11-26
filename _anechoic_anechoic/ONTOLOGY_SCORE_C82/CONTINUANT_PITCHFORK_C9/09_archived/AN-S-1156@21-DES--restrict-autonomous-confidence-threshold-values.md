---
atom_family: SPEC
atom_id: AN-S-1156
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 21
  updated_at: 2026-10-29 07:17:15 +0400
---
## Summary

Restrict Autonomous Confidence Threshold values

# Summary

Restrict Autonomous Confidence Threshold values

## Scope

Autonomous Confidence Threshold values.

## Claim

**every** Autonomous Confidence Threshold **must** be an integer percentage **`>=0`** **and** **`<=100`**. resolve its effective value from the applicable source under CA-M-271; the methodology **must not** restrict that value **to** a closed list of preferred percentages.

## Details
