---
atom_family: TKT
atom_id: AN-T-2439
container:
  component: C16
priority: 2
context:
  template: question
state:
  status: archived
  version: 1
  updated_at: 2026-10-05 07:34:12 +0000
---
## Summary

How to test before candidate runtime staging

# Summary

How to test before candidate runtime staging

## Concern

O164/O174 order the full suite before O175 candidate runtime/package staging, while execute_bound_release_suite currently requires the physical runtime-package directory. That implementation prerequisite makes the selected fresh-release path stop before the suite.

## Evidences

The suite helper already revalidates the exact candidate source frontier, compilation and complete package rows. E572@2 requires complete candidate package and full-suite proof before exposure and permits, but does not require, package preparation before the suite. O174 forbids runtime/package or Skill staging within this earlier phase.

## Blast radius

Only pre-staging suite admission and the fresh Release phase composition. Image admission, actual complete package verification, promotion and all permission gates remain unchanged.

## Decision

Options are hidden early staging, external manual pre-staging, or testing the exact bound source/compiled candidate before installation. Choose the third at90% confidence: validate all complete sealed candidate rows before execution; require exact package verification when a retained candidate package already exists, but do not create or require that package before testing. O175 subsequently stages/verifies those exact bytes, and image/promotion gates still require the complete package and successful suite evidence. P1702 owns the narrow correction and no-package/stale/tamper tests. Continue autonomously without a new Operator decision.

## Resolution

P1702 verifies exact source/compiled candidate rows before the declared suite without requiring or creating runtime/package staging. Existing package carriers remain strictly verified and actual image build still refuses before Docker until the complete package exists. Suite21/image37/promotion14 focused cases pass. P1701's fresh ten-phase disposable path also passes without external pre-staging; O175 alone performs package staging after the passed suite. No hidden install or Project/Skill exposure is introduced.
