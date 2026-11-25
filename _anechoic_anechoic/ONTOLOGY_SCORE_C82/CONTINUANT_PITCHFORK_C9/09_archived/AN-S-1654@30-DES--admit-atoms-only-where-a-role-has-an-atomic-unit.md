---
atom_family: SPEC
atom_id: AN-S-1654
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 30
  updated_at: 2026-10-29 07:45:27 +0400
---
## Summary

Admit Atoms only where a role has an atomic unit

## Claim scope

Content Role Type admission.

## Claim

a Content Role admits a Type value for an Atom **only** **when** that role has an independently governed atomic unit that benefits from stable identity, admission, **and** whole-unit lifecycle; ANECHOIC **must not** create a placeholder Type value merely **to** fill a semantic coordinate.

## Details

Every Current Atom has exactly one substantive admitted Type under its Content Role. A Draft Atom may remain incomplete while being authored. A Type value must not be invented merely to fill a semantic coordinate, and a Content Role name must not be copied as a Type value. This rule does not constrain Type values to a particular numeric Tier. General-name Type fields whose admission or full Subject path is not established remain uncovered and held; this rule does not claim that all Subject paths are complete.
