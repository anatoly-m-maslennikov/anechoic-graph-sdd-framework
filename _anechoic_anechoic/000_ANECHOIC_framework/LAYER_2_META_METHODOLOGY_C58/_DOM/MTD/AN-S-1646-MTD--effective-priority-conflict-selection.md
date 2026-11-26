---
atom_family: SPEC
atom_id: AN-S-1646
container:
  component: C58
tier: 3
context:
  lens: DOM/MTD
state:
  status: active
  version: 40
  updated_at: '2026-11-25T20:21:09.091992+00:00'
---
## Summary

Effective priority conflict selection

## Claim

Compare competing Tickets under the applicable Operator-selected priority policy. Read each integer Priority from the Ticket Header under AN-S-3169. Use the selected criteria and effective parameters. Component ancestry supplies no implicit priority increment.

Ask the Operator by default. An admitted automatic selection can proceed when the criteria identify exactly one eligible winner. Ask when the candidates tie, are incomparable, or lack evidence. Stop when external obligations cannot be satisfied together. Apply Tier authority, replacement, and scoped overrides under their own rules.
