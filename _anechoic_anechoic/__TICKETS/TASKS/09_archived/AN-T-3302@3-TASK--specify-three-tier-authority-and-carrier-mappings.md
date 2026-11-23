---
atom_family: TKT
atom_id: AN-T-3302
container:
  component: C9
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 3
  updated_at: 2026-10-24 06:04:39 +0400
---
## Summary

Specify three-tier authority and Carrier mappings

# Specify three-tier authority and Carrier mappings

the Assignee **must** specify the complete authority **and** Carrier mappings required by Core / General / Standard.

## Scope

(the active methodology rules for Local Tier eligibility, Global Tier derivation, Goal placement, Content Role **and** Type tier restrictions, tier parentage, **and** tier serialization)

## Definition of Done

the Task is **not** Done **if** (an admitted structural case lacks an explicit old-to-new authority mapping **or** Goal placement **or** a Content Role **or** Type restriction is unmapped **or** default omission, tier labels, **or** filename tokens are ambiguous **or** changed precedence is hidden as a naming change **or** lower-tier source authority becomes freely replaceable by an Extension **or** Local Configuration).

## Details

FX-04: consume the Scope specification from CA-P-953. use the accepted hierarchy: Core foundations **and** invariants; General shared specifications independent of concrete representation **or** implementation; Standard concrete fields, syntax, procedures, **and** test cases. Standard (STD) remains the lowest Local Tier **and** the omitted default. use CORE **and** GENERAL for explicit tier tokens. derive Global Tier mappings from the accepted structural hierarchy **and** ordered Local Tiers; this derivation requires **no** separate approval of tier arithmetic. reconcile the current Project Principle/Core/Standard ladder, external Goal exception, recursive child mapping, Core-only Implementation Method, **and** existing Standard-only Implementation Decision restrictions against the new hierarchy. preserve Project-only Principle eligibility; do **not** introduce another Principle tier. consult Project Principles **before** escalating a genuinely unresolved policy choice below the effective Autonomous Confidence Threshold. earlier execution evidence retains historical tier names; map its middle Standard to General **and** its lowest Detail to Standard, **not** its inventory of existing pre-change Standard Atoms.
